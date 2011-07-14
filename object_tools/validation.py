from django.core.exceptions import ImproperlyConfigured
from django.db import models

__all__ = ['validate']

def validate(tool_class, model_class):
    """
    Does basic ObjectTool option validation. 
    """
    # Before we can introspect models, they need to be fully loaded so that
    # inter-relations are set up correctly. We force that here.
    #models.get_apps()
    
    if not hasattr(tool_class, 'name'):
        raise ImproperlyConfigured("No 'name' attribute found for tool %s." % tool_class.__name__)
    
    if not hasattr(tool_class, 'label'):
        raise ImproperlyConfigured("No 'label' attribute found for tool %s." % tool_class.__name__)
    
    if not hasattr(tool_class, 'form_class'):
        raise ImproperlyConfigured("No 'form_class' attribute found for tool %s." % tool_class.__name__)

    if not hasattr(tool_class, 'view'):
        raise NotImplementedError("'view' method not implemented for tool %s." % tool_class.__name__)
