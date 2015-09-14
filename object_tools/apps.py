from django.apps import config


class SimpleObjectToolsAppConfig(config.AppConfig):
    """Simple AppConfig which does not do automatic discovery."""
    name = "object_tools"


class ObjectToolsAppConfig(SimpleObjectToolsAppConfig):
    """The default AppConfig for object_tools which does autodiscovery."""
    def ready(self):
        super(ObjectToolsAppConfig, self).ready()
        self.module.autodiscover()
