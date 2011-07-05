from django.core.exceptions import ImproperlyConfigured
from django.db.models import get_models

class AlreadyRegistered(Exception):
    pass

class ObjectTools(object):
    """
    An ObjectTools object providsing various objecttools for various model classes.
    Models are registered with the AdminSite using the register() method.
    """
    name = 'object-tools'
    app_name = 'object-tools'
    
    def __init__(self):
        self._registry = {} # model class -> object_tools instance

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

        if not model_class:
            models = get_models()
        else:
            models = [model_class,]

        for model in models:
            if model._meta.abstract:
                raise ImproperlyConfigured('The model %s is abstract, so it '
                      'cannot be registered with object tools.' % model.__name__)

            if model in self._registry:
                raise AlreadyRegistered('The model %s is already registered' % model.__name__)

            # Instantiate the object_tools class to save in the registry
            if self._registry.has_key(model):
                self._registry[model].append(object_tool_class(model))
            else:
                self._registry[model] = [object_tool_class(model),]
    
    def get_urls(self):
        from django.conf.urls.defaults import patterns, url, include

        urlpatterns = patterns('',)

        # Add in each object_tool's views.
        for model, object_tools in self._registry.iteritems():
            for object_tool in object_tools:
                urlpatterns += patterns('',
                    url(r'^%s/%s/' % (model._meta.app_label, model._meta.module_name),
                        include(object_tool.urls))
                )

        return urlpatterns

    @property
    def urls(self):
        return self.get_urls(), self.app_name, self.name

# This global object represents the default object tools, for the common case.
# You can instantiate ObjectTools in your own code to create a custom object tools object.
tools = ObjectTools()
