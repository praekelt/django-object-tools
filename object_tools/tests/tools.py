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
    form_class = TestMediaForm

    def view(self):
        pass


class TestInvalidTool(object_tools.ObjectTool):
    pass


object_tools.tools.register(TestTool)
object_tools.tools.register(TestMediaTool)
