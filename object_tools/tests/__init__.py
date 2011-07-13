import sys
from unittest import TestCase

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured

from object_tools import autodiscover
from object_tools.options import ObjectTool
from object_tools.sites import ObjectTools
from object_tools.tests.tools import TestForm, TestTool, TestMediaTool, TestInvalidTool
from object_tools.validation import validate

class MockRequest():
    method = 'POST'
    POST = ()

class InitTestCase(TestCase):
    def test_autodiscover(self):
        autodiscover()
        self.failUnless('object_tools.tests.tools' in sys.modules.keys(), 'Autodiscover should import tool modules from installed apps.')

class ValidateTestCase(TestCase):
    """
    Testcase testing object_tools.validation ObjectTool validation.
    """
    def test_validation(self):
        # Fail without 'name' member.
        self.failUnlessRaises(ImproperlyConfigured, validate, TestInvalidTool, ContentType)
        try:
            validate(TestInvalidTool, ContentType)
        except ImproperlyConfigured, e:
            self.failUnlessEqual(e.message, "No 'name' attribute found for tool TestInvalidTool.")

        TestInvalidTool.name = 'test_invalid_tool'
        
        # Fail without 'form_class' member.
        self.failUnlessRaises(ImproperlyConfigured, validate, TestInvalidTool, ContentType)
        try:
            validate(TestInvalidTool, ContentType)
        except ImproperlyConfigured, e:
            self.failUnlessEqual(e.message, "No 'form_class' attribute found for tool TestInvalidTool.")

        TestInvalidTool.form_class = TestForm
        #validate(TestInvalidTool, ContentType)

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

class ObjectToolTestCase(TestCase):
    """
    Testcase for object_tools.options.ObjectTool.
    """
    def test_init(self):
        tool = ObjectTool(ContentType)
        self.failUnless(tool.model == ContentType, 'Object Tool should have self.model set on init.')

    def test_construct_form(self):
        # Tool should provide form class.
        tool = ObjectTool(ContentType)
        self.failUnlessRaises(AttributeError, tool.construct_form, MockRequest())
        tool = TestTool(ContentType)
        tool.construct_form(MockRequest())

    def test_media(self):
        tool = TestTool(ContentType)
        form = tool.construct_form(MockRequest())
        media = tool.media(form)
        
        #Media result should include default admin media.
        self.failUnlessEqual(media.render_js(), [u'<script type="text/javascript" src="/media/js/core.js"></script>', u'<script type="text/javascript" src="/media/js/admin/RelatedObjectLookups.js"></script>', u'<script type="text/javascript" src="/media/js/jquery.min.js"></script>', u'<script type="text/javascript" src="/media/js/jquery.init.js"></script>'], 'Media result should include default admin media.')

        tool = TestMediaTool(ContentType)
        form = tool.construct_form(MockRequest())
        media = tool.media(form)
        
        #Media result should also include field specific media.
        self.failUnlessEqual(media.render_js(), [u'<script type="text/javascript" src="/media/js/core.js"></script>', u'<script type="text/javascript" src="/media/js/admin/RelatedObjectLookups.js"></script>', u'<script type="text/javascript" src="/media/js/jquery.min.js"></script>', u'<script type="text/javascript" src="/media/js/jquery.init.js"></script>', u'<script type="text/javascript" src="/media/js/calendar.js"></script>', u'<script type="text/javascript" src="/media/js/admin/DateTimeShortcuts.js"></script>'])

    def test_reverse(self):
        tool = TestTool(ContentType)
        self.failUnlessEqual(tool.reverse(), '/object-tools/contenttypes/contenttype/test_tool/', "Tool url reverse should reverse similar to how admin does, except pointing to the particular tool.")
        
        tool = TestMediaTool(ContentType)
        self.failUnlessEqual(tool.reverse(), '/object-tools/contenttypes/contenttype/test_media_tool/', "Tool url reverse should reverse similar to how admin does, except pointing to the particular tool.")

    def test_urls(self):
        tool = TestTool(ContentType)
        urls = tool.urls
        self.failUnlessEqual(len(urls), 1, 'urls property should only return 1 url') 
        self.failUnlessEqual(urls[0].__repr__(), '<RegexURLPattern contenttypes_contenttype_test_tool ^test_tool/$>')
        self.failUnlessEqual(urls[0].name, 'contenttypes_contenttype_test_tool', 'URL should be named as "<app_label>_<module_name>_<tool_name>".')

