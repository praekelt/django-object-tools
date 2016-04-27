"""Handle future url tag deprecation so we don't leave pre Django 1.8 in either
an unmaintained state or in a different branch."""

from django.template import Library

try:
    # Pre 1.8
    from django.templatetags.future import url as base_url
except ImportError:
    from django.template.defaulttags import url as base_url


register = Library()


@register.tag
def url(parser, token):
    return base_url(parser, token)
