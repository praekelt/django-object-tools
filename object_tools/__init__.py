from object_tools.options import ObjectTool
from object_tools.sites import tools

def autodiscover():
    """
    Auto-discover INSTALLED_APPS obj_tools.py modules and fail silently when
    not present. This forces an import on them to register any object tools they
    may want.
    """
    from django.conf import settings
    from django.utils.importlib import import_module
    from django.utils.module_loading import module_has_submodule

    for app in settings.INSTALLED_APPS:
        mod = import_module(app)
        # Attempt to import the app's obj_tools module.
        try:
            import_module('%s.obj_tools' % app)
        except:
            # Decide whether to bubble up this error. If the app just
            # doesn't have an obj_tools module, we can ignore the error
            # attempting to import it, otherwise we want it to bubble up.
            if module_has_submodule(mod, 'obj_tools'):
                raise
