from django.contrib.auth.models import User
from django.template import Template, Context
from django.test import TestCase, RequestFactory


class ObjectToolsInclusionTagsTestCase(TestCase):
    """
    Testcase for object_tools.templatetags.object_tools_inclusion_tags.
    """
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='test_user')

    def test_object_tools(self):
        request = self.factory.get('/')
        request.user = self.user
        context = Context({
            'model': User,
            'request': request,
        })
        t = Template("{% load object_tools_inclusion_tags %}{% object_tools \
                model request.user %}")

        # Anon user should not have any tools.
        result = t.render(context)
        expected_result = '\n'
        self.assertEqual(result, expected_result)

        # User without permissions should not have any tools.
        user = User()
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
class="historylink">Test Media Tool</a></li>\n\n'
        self.assertEqual(result, expected_result)

    def tearDown(self):
        self.user.delete()
