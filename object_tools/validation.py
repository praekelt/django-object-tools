from django.core.exceptions import ImproperlyConfigured

__all__ = ['validate']


def validate(tool_class, model_class):
    """
    Does basic ObjectTool option validation.
    """
    if not hasattr(tool_class, 'name'):
        raise ImproperlyConfigured("No 'name' attribute found for tool %s."\
                % tool_class.__name__)

    if not hasattr(tool_class, 'label'):
        raise ImproperlyConfigured("No 'label' attribute found for tool %s."\
                % tool_class.__name__)

    if not hasattr(tool_class, 'view'):
        raise NotImplementedError("'view' method not implemented for tool %s."\
                % tool_class.__name__)
