from __future__ import unicode_literals

import django
from object_tools.options import ObjectTool
from object_tools.sites import tools


def old_autodiscover():
    """
    Auto-discover INSTALLED_APPS tools.py modules and fail silently when
    not present. This forces an import on them to register any object
    tools they may want.
    """
    from django.conf import settings
    from django.utils.importlib import import_module
    from django.utils.module_loading import module_has_submodule

    for app in settings.INSTALLED_APPS:
        mod = import_module(app)
        # Attempt to import the app's tools module.
        try:
            import_module('%s.tools' % app)
        except:
            # Decide whether to bubble up this error. If the app just
            # doesn't have an tools module, we can ignore the error
            # attempting to import it, otherwise we want it to bubble up.
            if module_has_submodule(mod, 'tools'):
                raise


def autodiscover():
    if django.VERSION < (1, 7):
        old_autodiscover()
    else:
        from django.utils.module_loading import autodiscover_modules
        autodiscover_modules('tools', register_to=tools)

default_app_config = 'object_tools.apps.ObjectToolsAppConfig'
