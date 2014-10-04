from django.apps import config


class ObjectToolsAppConfig(config.AppConfig):
    name = "object_tools"

    def ready(self):
        pass
