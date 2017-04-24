from __future__ import unicode_literals

import sys
from unittest import TestCase

from django import template
from django.test import TestCase as TC
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.template import Template

try:
    from django.test.client import RequestFactory
except ImportError:
    from snippetscream import RequestFactory


# Since this module gets imported in the application's root package, it cannot
# import models from other applications at the module level.  That means User
# is imported in each test class.

from object_tools import autodiscover
from object_tools.options import ObjectTool
from object_tools.sites import ObjectTools
from object_tools.tests.tools import TestTool, TestMediaTool, TestInvalidTool
from object_tools.validation import validate


class MockRequest():
    method = 'POST'
    POST = ()
    FILES = ()


class InitTestCase(TestCase):
    def test_autodiscover(self):
        autodiscover()
        self.assertTrue(
            'object_tools.tests.tools' in list(sys.modules.keys()),
            'Autodiscover should import tool modules from installed apps.'
        )


class ValidateTestCase(TestCase):
    """
    Testcase testing object_tools.validation ObjectTool validation.
    """

    @classmethod
    def setUpClass(cls):
        from django.contrib.auth.models import User
        cls.user_klass = User

    def test_validation(self):
        # Fail without 'name' member.
        self.assertRaises(
            ImproperlyConfigured, validate, TestInvalidTool, self.user_klass
        )
        try:
            validate(TestInvalidTool, self.user_klass)
        except ImproperlyConfigured as e:
            message = str(e)
            self.assertEqual(
                message, "No 'name' attribute found for tool TestInvalidTool."
            )

        TestInvalidTool.name = 'test_invalid_tool'

        # Fail without 'label' member.
        self.assertRaises(
            ImproperlyConfigured, validate, TestInvalidTool, self.user_klass
        )
        try:
            validate(TestInvalidTool, self.user_klass)
        except ImproperlyConfigured as e:
            message = str(e)
            self.assertEqual(
                message,
                "No 'label' attribute found for tool TestInvalidTool."
            )

        TestInvalidTool.label = 'Test Invalid Tool'

        # Fail without 'view' member.
        self.assertRaises(
            NotImplementedError, validate, TestInvalidTool, self.user_klass
        )
        try:
            validate(TestInvalidTool, self.user_klass)
        except NotImplementedError as e:
            message = str(e)
            self.assertEqual(
                message, "No 'view' method found for tool TestInvalidTool."
            )


class ObjectToolsInclusionTagsTestCase(TestCase):
    """
    Testcase for object_tools.templatetags.object_tools_inclusion_tags.
    """

    @classmethod
    def setUpClass(cls):
        from django.contrib.auth.models import User
        cls.user_klass = User

    def setUp(self):
        self.factory = RequestFactory()
        self.user = self.user_klass.objects.create_user(username='test_user')

    def test_object_tools(self):
        autodiscover()
        request = self.factory.get('/')
        request.user = self.user
        context = template.Context({
            'model': self.user_klass,
            'request': request,
        })
        t = Template("{% load object_tools_inclusion_tags %}{% object_tools \
                model request.user %}")

        # Anon user should not have any tools.
        result = t.render(context)
        expected_result = '\n'
        self.assertEqual(result, expected_result)

        # User without permissions should not have any tools.
        user = self.user_klass()
        user.save()
        context['request'].user = user
        result = t.render(context)
        expected_result = '\n'
        self.assertEqual(result, expected_result)

        # Superuser should have tools.
        user.is_superuser = True
        user.save()
        result = t.render(context)
        expected_result = '\n<li><a href="/object-tools/auth/user/\
test_tool/?" title=""class="historylink">Test Tool</a></li>\n\n\
<li><a href="/object-tools/auth/user/test_media_tool/?" title=""\
class="historylink"></a></li>\n\n'
        self.assertEqual(result, expected_result)

    def tearDown(self):
        self.user.delete()


class ObjectToolsTestCase(TestCase):
    """
    Testcase for object_tools.sites.ObjectTools.
    """
    def test__init(self):
        # Check init results in expected members.
        tools = ObjectTools()
        self.assertEqual(tools.name, 'object-tools')
        self.assertEqual(tools.app_name, 'object-tools')
        self.assertEqual(tools._registry, {})

    def test_register(self):
        # Set DEBUG = True so validation is triggered.
        from django.conf import settings
        settings.DEBUG = True

        tools = ObjectTools()
        tools.register(TestTool)

    def test_urls(self):
        tools = ObjectTools()
        # Without any tools should be empty list, namespaces
        # should be 'object-tools'.
        self.assertEqual(tools.urls, ([], 'object-tools', 'object-tools'))

        # With a tool registered, urls should include it for each model.
        tools.register(TestTool)
        urls = tools.urls
        self.assertEqual(len(urls[0]), 6)
        for url in urls[0]:
            self.assertTrue(url.url_patterns[0].__repr__() in [
                '<RegexURLPattern sessions_session_test_tool ^test_tool/$>',
                '<RegexURLPattern auth_user_test_tool ^test_tool/$>',
                '<RegexURLPattern auth_group_test_tool ^test_tool/$>',
                '<RegexURLPattern auth_permission_test_tool ^test_tool/$>',
                '<RegexURLPattern contenttypes_contenttype_test_tool ^test_tool/$>',
                '<RegexURLPattern admin_logentry_test_tool ^test_tool/$>'
            ])


class ObjectToolTestCase(TestCase):
    """
    Testcase for object_tools.options.ObjectTool.
    """

    @classmethod
    def setUpClass(cls):
        from django.contrib.auth.models import User
        cls.user_klass = User

    def setUp(self):
        self.factory = RequestFactory()
        self.user = self.user_klass.objects.create_user(username='test_user')

    def test_init(self):
        tool = ObjectTool(self.user_klass)
        self.assertTrue(tool.model == self.user_klass, 'Object Tool should have \
                self.model set on init.')

    def test_construct_context(self):
        request = self.factory.get('/')
        request.user = self.user
        tool = TestTool(self.user_klass)
        context = tool.construct_context(request)

        # Do a very basic check to see if values are in fact constructed.
        for key, value in context.items():
            self.assertTrue(value)

    def test_construct_form(self):
        tool = ObjectTool(self.user_klass)
        tool = TestTool(self.user_klass)
        tool.construct_form(MockRequest())

    def test_media(self):
        tool = TestTool(self.user_klass)
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

        tool = TestMediaTool(self.user_klass)
        form = tool.construct_form(MockRequest())
        media = tool.media(form)

        #Media result should also include field specific media.
        self.assertEqual(media.render_js(), [
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
        ])

    def test_reverse(self):
        tool = TestTool(self.user_klass)
        self.assertEqual(tool.reverse(), '/object-tools/auth/user/\
test_tool/', "Tool url reverse should reverse similar to \
how admin does, except pointing to the particular tool.")

        tool = TestMediaTool(self.user_klass)
        self.assertEqual(tool.reverse(), '/object-tools/auth/user/\
test_media_tool/', "Tool url reverse should reverse similar \
to how admin does, except pointing to the particular tool.")

    def test_urls(self):
        tool = TestTool(self.user_klass)
        urls = tool.urls
        self.assertEqual(len(urls), 1, 'urls property should only \
                return 1 url')
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
        tool = TestTool(self.user_klass)
        self.assertRaises(PermissionDenied, tool._view, request)

        # Should raise permission denied for user without permissions.
        self.assertRaises(PermissionDenied, tool._view, request)

        # Should not raise permission denied for super user.
        request.user.is_superuser = True
        request.user.save()
        tool._view(request)

    def tearDown(self):
        self.user.delete()


class ChangeViewTestCase(TC):

    def test_it(self):
        from django.contrib.auth.models import User
        User.objects.create_superuser(username="testuser", password="0000", email="testuser@example.com")
        self.client.login(username="testuser", password="0000")
        response = self.client.get("/admin/auth/user/")
        tool_html = '<li><a href="/object-tools/auth/user/test_tool/?" ' \
                    'title=""class="historylink">Test Tool</a></li>'
        self.assertContains(response, tool_html)
