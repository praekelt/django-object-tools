from django import forms

from django.contrib.admin.widgets import AdminSplitDateTime

import object_tools

class TestForm(forms.Form):
    pass

class TestMediaForm(forms.Form):
    media_field = forms.fields.DateTimeField(
        widget = AdminSplitDateTime,
    )

class TestTool(object_tools.ObjectTool):
    name = 'test_tool'
    form_class = TestForm
    pass

class TestMediaTool(object_tools.ObjectTool):
    name = 'test_media_tool'
    form_class = TestMediaForm

class TestInvalidTool(object_tools.ObjectTool):
    pass

object_tools.tools.register(TestTool)
object_tools.tools.register(TestMediaTool)
