from django import template

from object_tools import tools

register = template.Library()

@register.inclusion_tag('object_tools/inclusion_tags/object_tools.html')
def object_tools(cl):
    model = cl.model
    
    if tools._registry.has_key(model):
        object_tool_classes = tools._registry[model]
    else:
        object_tools = []

    object_tools = [object_tool for object_tool in object_tool_classes]
    return {'object_tools': object_tools}
