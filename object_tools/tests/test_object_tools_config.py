from __future__ import unicode_literals

import sys

import django
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase

from object_tools import autodiscover
from object_tools.sites import ObjectTools
from object_tools.tests.tools import TestTool, TestInvalidTool
from object_tools.validation import validate


class InitTestCase(TestCase):
    """
    Test that tool modules are imported after autodiscover()
    """
    def test_autodiscover(self):
        autodiscover()
        self.assertTrue(
            'object_tools.tests.tools' in list(sys.modules.keys()),
            'Autodiscover should import tool modules from installed apps.'
        )


class ValidateTestCase(TestCase):
    """
    Test object tool validation.
    Each object tool should have name and a label attribute.
    Each object tool should also define a view method.
    ImproperlyConfigured exception is raised for missing name and/or label.
    NotImplementedError is raised if a view is not defined.
    """

    def test_validation(self):
        # Fail without 'name' member.
        self.assertRaises(
            ImproperlyConfigured, validate, TestInvalidTool, User
        )
        try:
            validate(TestInvalidTool, User)
        except ImproperlyConfigured as e:
            message = str(e)
            self.assertEqual(
                message, "No 'name' attribute found for tool TestInvalidTool."
            )

        TestInvalidTool.name = 'test_invalid_tool'

        # Fail without 'label' member.
        self.assertRaises(
            ImproperlyConfigured, validate, TestInvalidTool, User
        )
        try:
            validate(TestInvalidTool, User)
        except ImproperlyConfigured as e:
            message = str(e)
            self.assertEqual(
                message,
                "No 'label' attribute found for tool TestInvalidTool."
            )

        TestInvalidTool.label = 'Test Invalid Tool'

        # Fail without 'view' member.
        self.assertRaises(
            NotImplementedError, validate, TestInvalidTool, User
        )
        try:
            validate(TestInvalidTool, User)
        except NotImplementedError as e:
            message = str(e)
            self.assertEqual(
                message, "No 'view' method found for tool TestInvalidTool."
            )


class ObjectToolsTestCase(TestCase):
    """
    Testcase for object_tools.sites.ObjectTools.
    """
    def test_init(self):
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

        if django.VERSION >= (2, 0):
            urlpatterns = [
                "<URLPattern '^test_tool/$' [name='sessions_session_test_tool']>",
                "<URLPattern '^test_tool/$' [name='auth_user_test_tool']>",
                "<URLPattern '^test_tool/$' [name='auth_group_test_tool']>",
                "<URLPattern '^test_tool/$' [name='auth_permission_test_tool']>",
                "<URLPattern '^test_tool/$' [name='contenttypes_contenttype_test_tool']>",
                "<URLPattern '^test_tool/$' [name='admin_logentry_test_tool']>",
            ]
        else:
            urlpatterns = [
                '<RegexURLPattern sessions_session_test_tool ^test_tool/$>',
                '<RegexURLPattern auth_user_test_tool ^test_tool/$>',
                '<RegexURLPattern auth_group_test_tool ^test_tool/$>',
                '<RegexURLPattern auth_permission_test_tool ^test_tool/$>',
                '<RegexURLPattern contenttypes_contenttype_test_tool ^test_tool/$>',
                '<RegexURLPattern admin_logentry_test_tool ^test_tool/$>'
            ]

        for url in urls[0]:
            self.assertTrue(url.url_patterns[0].__repr__() in urlpatterns)
