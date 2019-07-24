from __future__ import unicode_literals

from django.contrib.auth import models as auth_app
from django.db import DEFAULT_DB_ALIAS
from django.db.models import signals

import object_tools


def _get_permission_codename(tool, opts):
    return '%s_%s' % (tool.name, opts.object_name.lower())


def _get_all_permissions(opts, tools):
    """Returns (codename, name) for all tools."""
    perms = []
    for tool in tools:
        perms.append((_get_permission_codename(tool, opts), 'Can %s %s' % \
                (tool.name, opts.verbose_name_plural)))
    return perms


def _create_permissions(**kwargs):
    """
    Almost exactly the same as django.contrib.auth.management.__init__.py
    """
    from django.contrib.contenttypes.models import ContentType

    object_tools.autodiscover()
    tools = object_tools.tools._registry

    # This will hold the permissions we're looking for as
    # (content_type, (codename, name))
    searched_perms = list()
    # The codenames and ctypes that should exist.
    ctypes = set()
    for model, tools in tools.items():
        ctype = ContentType.objects.get_for_model(model)
        ctypes.add(ctype)
        for perm in _get_all_permissions(model._meta, tools):
            searched_perms.append((ctype, perm))

    # Find all the Permissions that have a context_type for a model we're
    # looking for.  We don't need to check for codenames since we already have
    # a list of the ones we're going to create.
    all_perms = set(auth_app.Permission.objects.filter(
        content_type__in=ctypes,
    ).values_list(
        "content_type", "codename"
    ))

    for ctype, (codename, name) in searched_perms:
        # If the permissions exists, move on.
        if (ctype.pk, codename) in all_perms:
            continue
        p = auth_app.Permission.objects.create(
            codename=codename,
            name=name,
            content_type=ctype
        )
        if kwargs.get("verbosity", 2) >= 2:
            print("Adding permission '%s'" % p)


def create_permissions(app_config, verbosity=2, interactive=True, using=DEFAULT_DB_ALIAS, **kwargs):
    return _create_permissions(verbosity=verbosity, interactive=True, using=DEFAULT_DB_ALIAS, **kwargs)


signals.post_migrate.connect(
    create_permissions,
    dispatch_uid="object_tools.management.create_permissions"
)
