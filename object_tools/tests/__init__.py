import sys
from unittest import TestCase

from django import template
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.template import Template

from snippetscream import RequestFactory

from object_tools import autodiscover
from object_tools.options import ObjectTool
from object_tools.sites import ObjectTools
from object_tools.tests.tools import TestTool, TestMediaTool, TestInvalidTool
from object_tools.validation import validate


class MockRequest():
    method = 'POST'
    POST = ()


class InitTestCase(TestCase):
    def test_autodiscover(self):
        autodiscover()
        self.failUnless('object_tools.tests.tools' in sys.modules.keys(), \
                'Autodiscover should import tool modules from installed apps.')


class ValidateTestCase(TestCase):
    """
    Testcase testing object_tools.validation ObjectTool validation.
    """
    def test_validation(self):
        # Fail without 'name' member.
        self.failUnlessRaises(ImproperlyConfigured, validate, \
                TestInvalidTool, User)
        try:
            validate(TestInvalidTool, User)
        except ImproperlyConfigured, e:
            self.failUnlessEqual(e.message, \
                    "No 'name' attribute found for tool TestInvalidTool.")

        TestInvalidTool.name = 'test_invalid_tool'

        # Fail without 'label' member.
        self.failUnlessRaises(ImproperlyConfigured, validate, \
                TestInvalidTool, User)
        try:
            validate(TestInvalidTool, User)
        except ImproperlyConfigured, e:
            self.failUnlessEqual(e.message, \
                    "No 'label' attribute found for tool TestInvalidTool.")

        TestInvalidTool.label = 'Test Invalid Tool'

        # Fail without 'view' member.
        self.failUnlessRaises(NotImplementedError, validate, TestInvalidTool, \
                User)
        try:
            validate(TestInvalidTool, User)
        except NotImplementedError, e:
            self.failUnlessEqual(e.message, \
                    "'view' method not implemented for tool TestInvalidTool.")


class ObjectToolsInclusionTagsTestCase(TestCase):
    """
    Testcase for object_tools.templatetags.object_tools_inclusion_tags.
    """
    def test_object_tools(self):
        autodiscover()
        context = template.Context({
            'model': User,
            'request': RequestFactory().get('/'),
        })
        t = Template("{% load object_tools_inclusion_tags %}{% object_tools \
                model request.user %}")

        # Anon user should not have any tools.
        result = t.render(context)
        expected_result = '\n'
        self.failUnlessEqual(result, expected_result)

        # User without permissions should not have any tools.
        user = User()
        user.save()
        context['request'].user = user
        result = t.render(context)
        expected_result = '\n'
        self.failUnlessEqual(result, expected_result)

        # Superuser should have tools.
        user.is_superuser = True
        user.save()
        result = t.render(context)
        expected_result = u'\n    <li><a href="/object-tools/auth/user/\
test_tool/" title=""class="historylink">Test Tool</a></li>\n\n    \
<li><a href="/object-tools/auth/user/test_media_tool/" title=""\
class="historylink"></a></li>\n\n'
        self.failUnlessEqual(result, expected_result)


class ObjectToolsTestCase(TestCase):
    """
    Testcase for object_tools.sites.ObjectTools.
    """
    def test__init(self):
        # Check init results in expected members.
        tools = ObjectTools()
        self.failUnlessEqual(tools.name, 'object-tools')
        self.failUnlessEqual(tools.app_name, 'object-tools')
        self.failUnlessEqual(tools._registry, {})

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
        self.failUnlessEqual(tools.urls, ([], 'object-tools', 'object-tools'))

        # With a tool registered, urls should include it for each model.
        tools.register(TestTool)
        urls = tools.urls
        self.failUnlessEqual(len(urls[0]), 8)
        for url in urls[0]:
            self.failUnless(url.__repr__() in [
            '<RegexURLResolver [<RegexURLPattern auth_message_test_tool \
^test_tool/$>] (None:None) ^auth/message/>',
            '<RegexURLResolver [<RegexURLPattern auth_group_test_tool \
^test_tool/$>] (None:None) ^auth/group/>',
            '<RegexURLResolver [<RegexURLPattern contenttypes_contenttype\
_test_tool ^test_tool/$>] (None:None) ^contenttypes/contenttype/>',
            '<RegexURLResolver [<RegexURLPattern sites_site_test_tool \
^test_tool/$>] (None:None) ^sites/site/>',
            '<RegexURLResolver [<RegexURLPattern auth_permission_test_tool \
^test_tool/$>] (None:None) ^auth/permission/>',
            '<RegexURLResolver [<RegexURLPattern auth_user_test_tool \
^test_tool/$>] (None:None) ^auth/user/>',
            '<RegexURLResolver [<RegexURLPattern sessions_session_test_tool \
^test_tool/$>] (None:None) ^sessions/session/>',
            '<RegexURLResolver [<RegexURLPattern admin_logentry_test_tool \
^test_tool/$>] (None:None) ^admin/logentry/>'
        ])


class ObjectToolTestCase(TestCase):
    """
    Testcase for object_tools.options.ObjectTool.
    """
    def test_init(self):
        tool = ObjectTool(User)
        self.failUnless(tool.model == User, 'Object Tool should have \
                self.model set on init.')

    def test_construct_context(self):
        request = RequestFactory().get('/')
        tool = TestTool(User)
        context = tool.construct_context(request)

        # Do a very basic check to see if values are in fact constructed.
        for key, value in context.iteritems():
            self.failUnless(value)

    def test_construct_form(self):
        tool = ObjectTool(User)
        tool = TestTool(User)
        tool.construct_form(MockRequest())

    def test_media(self):
        tool = TestTool(User)
        form = tool.construct_form(MockRequest())
        media = tool.media(form)

        #Media result should include default admin media.
        self.failUnlessEqual(media.render_js(), [u'<script type="\
text/javascript" src="/static/admin/js/core.js"></script>', \
u'<script type="text/javascript" src="/static/admin/js/admin/\
RelatedObjectLookups.js"></script>', u'<script type=\
"text/javascript" src="/static/admin/js/jquery.min.js">\
</script>', u'<script type="text/javascript" src=\
"/static/admin/js/jquery.init.js"></script>'], \
'Media result should include default admin media.')

        tool = TestMediaTool(User)
        form = tool.construct_form(MockRequest())
        media = tool.media(form)

        #Media result should also include field specific media.
        self.failUnlessEqual(media.render_js(), [
            u'<script type="text/javascript" src="/static/admin/js/\
core.js"></script>',
            u'<script type="text/javascript" src="/static/admin/js/\
admin/RelatedObjectLookups.js"></script>',
            u'<script type="text/javascript" src="/static/admin/js/\
jquery.min.js"></script>',
            u'<script type="text/javascript" src="/static/admin/js/\
jquery.init.js"></script>',
            u'<script type="text/javascript" src="/static/admin/js/\
calendar.js"></script>',
            u'<script type="text/javascript" src="/static/admin/js/\
admin/DateTimeShortcuts.js"></script>'
        ])

    def test_reverse(self):
        tool = TestTool(User)
        self.failUnlessEqual(tool.reverse(), '/object-tools/auth/user/\
test_tool/', "Tool url reverse should reverse similar to \
how admin does, except pointing to the particular tool.")

        tool = TestMediaTool(User)
        self.failUnlessEqual(tool.reverse(), '/object-tools/auth/user/\
test_media_tool/', "Tool url reverse should reverse similar \
to how admin does, except pointing to the particular tool.")

    def test_urls(self):
        tool = TestTool(User)
        urls = tool.urls
        self.failUnlessEqual(len(urls), 1, 'urls property should only \
                return 1 url')
        self.failUnlessEqual(urls[0].__repr__(),
            '<RegexURLPattern auth_user_test_tool ^test_tool/$>')
        self.failUnlessEqual(urls[0].name, 'auth_user_test_tool',
            'URL should be named as "<app_label>_<module_name>_<tool_name>\
                ".')

    def test_view(self):
        # Should raise permission denied on anonymous user.
        request = RequestFactory().get('/')
        tool = TestTool(User)
        self.failUnlessRaises(PermissionDenied, tool._view, request)

        # Should raise permission denied for user without permissions.
        user = User(username='test_view')
        user.save()
        request.user = user
        self.failUnlessRaises(PermissionDenied, tool._view, request)

        # Should not raise permission denied for super user.
        user.is_superuser = True
        user.save()
        request.user = user
        tool._view(request)
