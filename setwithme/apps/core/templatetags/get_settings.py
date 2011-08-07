# -*- coding: utf-8 -*-
from django import template
from django.conf import settings


register = template.Library()


@register.tag
def setting(parser, token):
    """
    Usage:
        {% load get_settings %}
        {% setting DEBUG %}
        {% setting DEBUG as debugging %}
    """
    split = token.split_contents()
    context_var = None
    option = None
    as_index = split.index('as') if 'as' in split else None

    if as_index is not None:
        try:
            context_var = split[as_index + 1]
        except IndexError:
            raise template.TemplateSyntaxError('Context variable assignment '
                                               'must take the form of {%% %s '
                                               'DEBUG as debugging %%}'
                                               % split[0])
        del split[as_index:as_index + 2]
    if len(split) == 2:
        option = split[1]
    else:
        raise template.TemplateSyntaxError('%s tag takes one required argument'
                                           ' with optional context_var'
                                           % split[0])

    return SettingNode(option=option, context_var=context_var)


class SettingNode(template.Node):
    def __init__(self, option, context_var=None):
        self.option = option
        self.context_var = context_var

    def render(self, context):
        # if FAILURE then FAIL silently
        try:
            value = getattr(settings, self.option)
            if self.context_var:
                context[self.context_var] = value
                return u''
            else:
                return str(value)
        except:
            return ''
