from __future__ import unicode_literals

import django
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.test import TestCase
from django.test.client import RequestFactory

from object_tools.options import ObjectTool
from object_tools.tests.tools import TestTool, TestMediaTool


class MockRequest(object):
    method = 'POST'
    POST = ()
    FILES = ()


class ObjectToolTestCase(TestCase):
    """
    Testcase for object_tools.options.ObjectTool.
    """
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='test_user')

    def test_init(self):
        tool = ObjectTool(User)
        self.assertTrue(
            tool.model == User,
            'Object Tool should have self.model set on init.'
        )

    def test_construct_context(self):
        request = self.factory.get('/')
        request.user = self.user
        tool = TestTool(User)
        context = tool.construct_context(request)

        # Do a very basic check to see if values are in fact constructed.
        for key, value in context.items():
            self.assertTrue(value)

    def test_construct_form(self):
        tool = TestTool(User)
        form = tool.construct_form(MockRequest())
        self.assertTrue(isinstance(form, tool.form_class))

    def test_media(self):
        tool = TestTool(User)
        form = tool.construct_form(MockRequest())
        media = tool.media(form)

        # Media result should include default admin media.
        self.assertEqual(media.render_js(), [
            '<script type="\
text/javascript" src="/static/admin/js/core.js"></script>',
            '<script type="text/javascript" src="/static/admin/js/admin/\
RelatedObjectLookups.js"></script>', '<script type=\
"text/javascript" src="/static/admin/js/jquery.min.js">\
</script>', '<script type="text/javascript" src=\
"/static/admin/js/jquery.init.js"></script>'
        ], 'Media result should include default admin media.')

        tool = TestMediaTool(User)
        form = tool.construct_form(MockRequest())
        media = tool.media(form)

        if django.VERSION >= (2, 0):
            media_js_list = [
                '<script type="text/javascript" src="/static/admin/js/\
core.js"></script>',
                '<script type="text/javascript" src="/static/admin/js/\
admin/RelatedObjectLookups.js"></script>',
                '<script type="text/javascript" src="/static/admin/js/\
jquery.min.js"></script>',
                '<script type="text/javascript" src="/static/admin/js/\
jquery.init.js"></script>',
                '<script type="text/javascript" src="/static/admin/js/\
vendor/jquery/jquery.min.js"></script>',
                '<script type="text/javascript" src="/static/admin/js/\
jquery.init.js"></script>',
                '<script type="text/javascript" src="/static/admin/js/\
calendar.js"></script>',
                '<script type="text/javascript" src="/static/admin/js/\
admin/DateTimeShortcuts.js"></script>'
            ]
        else:
            media_js_list = [
                '<script type="text/javascript" src="/static/admin/js/\
core.js"></script>',
                '<script type="text/javascript" src="/static/admin/js/\
admin/RelatedObjectLookups.js"></script>',
                '<script type="text/javascript" src="/static/admin/js/\
jquery.min.js"></script>',
                '<script type="text/javascript" src="/static/admin/js/\
jquery.init.js"></script>',
                '<script type="text/javascript" src="/static/admin/js/\
calendar.js"></script>',
                '<script type="text/javascript" src="/static/admin/js/\
admin/DateTimeShortcuts.js"></script>'
            ]

        # Media result should also include field specific media.
        self.assertEqual(media.render_js(), media_js_list)

    def test_reverse(self):
        tool = TestTool(User)
        self.assertEqual(tool.reverse(), '/object-tools/auth/user/\
test_tool/', "Tool url reverse should reverse similar to \
how admin does, except pointing to the particular tool.")

        tool = TestMediaTool(User)
        self.assertEqual(tool.reverse(), '/object-tools/auth/user/\
test_media_tool/', "Tool url reverse should reverse similar \
to how admin does, except pointing to the particular tool.")

    def test_urls(self):
        tool = TestTool(User)
        urls = tool.urls
        self.assertEqual(len(urls), 1, 'urls property should only \
                return 1 url')
        if django.VERSION >= (2, 0):
            self.assertEqual(
                urls[0].__repr__(),
                "<URLPattern '^test_tool/$' [name='auth_user_test_tool']>"
            )
        else:
            self.assertEqual(
                urls[0].__repr__(),
                '<RegexURLPattern auth_user_test_tool ^test_tool/$>'
            )
        self.assertEqual(
            urls[0].name, 'auth_user_test_tool',
            'URL should be named as "<app_label>_<model_name>_<tool_name>".'
        )

    def test_view(self):
        # Should raise permission denied on anonymous user.
        request = self.factory.get('/')
        request.user = self.user
        tool = TestTool(User)
        self.assertRaises(PermissionDenied, tool._view, request)

        # Should raise permission denied for user without permissions.
        self.assertRaises(PermissionDenied, tool._view, request)

        # Should not raise permission denied for super user.
        request.user.is_superuser = True
        request.user.save()
        tool._view(request)

    def tearDown(self):
        self.user.delete()
