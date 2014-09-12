import inspect

from django import template

from object_tools import tools

register = template.Library()


@register.inclusion_tag('object_tools/inclusion_tags/object_tools.html', takes_context=True)
def object_tools(context, model, user, exclude=None):
    if inspect.isclass(model):
        model_class = model
    else:
        model_class = model.__class__

    if model_class in tools._registry:
        object_tool_classes = tools._registry[model_class]
    else:
        object_tool_classes = []

    object_tools = [object_tool for object_tool in object_tool_classes]

    if exclude:
        object_tools.remove(exclude)

    allowed_tools = []
    for tool in object_tools:
        if tool.has_permission(user):
            allowed_tools.append(tool)

    ret_dict = {'object_tools': allowed_tools}
    if 'request' in context:
        ret_dict.update({
            'request': context['request']
        })

    return ret_dict
