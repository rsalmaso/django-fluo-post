# -*- coding: utf-8 -*-

# Copyright (C) 2007-2010, Salmaso Raffaele <raffaele@salmaso.org>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import datetime
from django import template
from django.template import TemplateSyntaxError, Library
from django.conf import settings
from django.db.models import Q
from django.utils.importlib import import_module
models = import_module('news.models')

register = template.Library()

class GetNewsNode(template.Node):
    def __init__(self, variable, category=None, order_by=None, limit=None, status=None):
        self.variable = variable
        self.limit = limit
        self.status = status
        self.category = category
        self.order_by = order_by

    def render(self, context):
        if self.status:
            kwargs = {'status': self.status}
        else:
            kwargs = {}

        if self.category:
            kwargs.update({'categories__name__in': self.category})

        news = models.News.objects.filter(**kwargs)
        if self.order_by:
            news = news.order_by(*self.order_by)

        # filter by pubblication date
        now = datetime.datetime.now()
        q1 = Q(pub_date_begin__lte=now) | Q(pub_date_begin__isnull=True)
        q2 = Q(pub_date_end__gte=now) | Q(pub_date_end__isnull=True)
        news = news.filter(q1 & q2)
        if self.limit:
            news = news[:self.limit]
        context[self.variable] = news
        return ''

def _get_news(parser, token, tag_name, status=None):
    args = token.split_contents()[1:]
    kwargs = {
        'as': None,
        'limit': None,
        'category': None,
        'order_by': None,
        'status': status,
    }
    kw = kwargs.keys()

    if len(args) < 2:
        raise TemplateSyntaxError, "'%s' requires at least 'as variable' (got %r)" % (tag_name, args)
    elif len(args) % 2 != 0:
        raise TemplateSyntaxError, "'%s' requires 'as variable' (got %r)" % (tag_name, args)
    i = 0
    while i < len(args):
        key = args[i]
        value = args[i+1]
        if key in kw:
            if key == 'limit':
                try:
                    value = int(value)
                except ValueError, err:
                    raise TemplateSyntaxError, "'%s' requires 'limit' to be a valid integer (got %r): %s" % (tag_name, value, err)
            elif key in ('order_by', 'category',):
                value = value.split(',')
            kwargs[key] = value
            i += 2
        else:
            raise TemplateSyntaxError, "'%s' unknown keyword (got %r)" % (tag_name, key)
    kwargs['variable'] = kwargs['as']
    kwargs.pop('as')
    return GetNewsNode(**kwargs)

@register.tag
def get_news(parser, token):
    """
    This will store a list of the news
    in the context.

    Usage::

        {% get_news as news %}
        {% get_news as news max 5 %}
        {% get_news as news category 'main'  %}
        {% get_news as news order_by '-date'  %}

        {% for item in news %}
        ...
        {% endfor %}
    """
    return _get_news(parser, token, 'get_news', None)

@register.tag
def get_published_news(parser, token):
    """
    This will store a list of the news
    in the context.

    Usage::

        {% get_published_news as news %}
        {% get_published_news as news max 5 %}
        {% get_published_news as news category 'main'  %}
        {% get_published_news as news order_by '-date'  %}

        {% for item in news %}
        ...
        {% endfor %}
    """
    return _get_news(parser, token, 'get_published_news', models.PUBLISHED)

@register.tag
def get_draft_news(parser, token):
    """
    This will store a list of the news
    in the context.

    Usage::

        {% get_draft_news as news %}
        {% get_draft_news as news max 5 %}
        {% get_draft_news as news category 'main'  %}
        {% get_draft_news as news order_by '-date'  %}

        {% for item in news %}
        ...
        {% endfor %}
    """
    return _get_news(parser, token, 'get_draft_news', models.DRAFT)

