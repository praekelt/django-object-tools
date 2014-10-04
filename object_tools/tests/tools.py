from django import forms

from django.contrib.admin.widgets import AdminSplitDateTime

import object_tools


class TestForm(forms.Form):
    pass


class TestMediaForm(forms.Form):
    media_field = forms.fields.DateTimeField(
        widget=AdminSplitDateTime,
    )


class TestTool(object_tools.ObjectTool):
    name = 'test_tool'
    label = 'Test Tool'
    form_class = TestForm

    def view(self, request, extra_context=None):
        pass


class TestMediaTool(object_tools.ObjectTool):
    name = 'test_media_tool'
    label = ''
    form_class = TestMediaForm

    def view(self):
        pass


class TestInvalidTool(object_tools.ObjectTool):
    pass


try:
    from django.apps import config
except ImportError:
    config = None

if config:
    def ready(cls):
        object_tools.tools.register(TestTool)
        object_tools.tools.register(TestMediaTool)
    object_tools.apps.ObjectToolsAppConfig.ready = ready

else:
    object_tools.tools.register(TestTool)
    object_tools.tools.register(TestMediaTool)
