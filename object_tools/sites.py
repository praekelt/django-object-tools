from __future__ import unicode_literals

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
try:
    from django.apps import apps
    get_models = apps.get_models
except ImportError:
    from django.db.models import get_models


class AlreadyRegistered(Exception):
    pass


class ObjectTools(object):
    """
    An ObjectTools object providing various object tools for various model
    classes. Models are registered with the ObjectTools using the
    register() method.
    """
    name = 'object-tools'
    app_name = 'object-tools'

    def __init__(self):
        self._registry = {}  # model class -> object_tools instance

    def register(self, object_tool_class, model_class=None):
        """
        Registers the given model(s) with the given object tool class.

        The model(s) should be Model classes, not instances.

        If a model class isn't given the object tool class will be registered
        for all models.

        If a model is already registered, this will raise AlreadyRegistered.

        If a model is abstract, this will raise ImproperlyConfigured.
        """
        if not object_tool_class:
            return None

        # Don't validate unless required.
        if object_tool_class and settings.DEBUG:
            from object_tools.validation import validate
            validate(object_tool_class, model_class)
            # = lambda model, adminclass: None

        if not model_class:
            models = get_models()
        else:
            models = [model_class, ]

        for model in models:
            if model._meta.abstract:
                raise ImproperlyConfigured(
                    'The model %s is abstract, so it \
                    cannot be registered with object tools.' % model.__name__)

            # Instantiate the object_tools class to save in the registry
            if model in self._registry:
                self._registry[model].append(object_tool_class(model))
            else:
                self._registry[model] = [object_tool_class(model), ]

    def get_urls(self):
        try:
            from django.conf.urls.defaults import url, include
        except ImportError:
            from django.urls import include, re_path

        urlpatterns = []

        # Add in each object_tool's views.
        for model, object_tools in self._registry.items():
            # to keep backward (Django <= 1.7) compatibility
            info = (model._meta.app_label,)
            try:
                info += (model._meta.model_name,)
            except AttributeError:
                info += (model._meta.module_name,)

            for object_tool in object_tools:
                urlpatterns.append(
                    re_path(r'^%s/%s/' % info, include(object_tool.urls))
                )
        return urlpatterns

    @property
    def urls(self):
        return self.get_urls(), self.app_name, self.name

# This global object represents the default object tools, for the common case.
# You can instantiate ObjectTools in your own code to create a
# custom object tools object.
tools = ObjectTools()
