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
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.template import TemplateSyntaxError, Library
from django.conf import settings
from django.db.models import Q
from django.utils.importlib import import_module
models = import_module('news.models')

register = template.Library()

class GetNewsListNode(template.Node):
    def __init__(self, name, category=None, order_by=None, limit=None, query_set=None, paginate_by=False):
        self.name = name
        self.limit = limit
        self.query_set = query_set
        self.category = category
        self.order_by = order_by
        self.paginate_by = paginate_by

    def _paginate(self, request, news_list, paginate_by):
        paginator = Paginator(news_list, paginate_by)

        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1

        try:
            news = paginator.page(page)
        except (EmptyPage, InvalidPage):
            news = paginator.page(paginator.num_pages)

        return news

    def render(self, context):
        news = self.query_set()

        if self.category:
            news = news.filter(categories__name__in=self.category)

        if self.order_by:
            news = news.order_by(*self.order_by)

        if self.limit:
            news = news[:self.limit]

        if self.paginate_by:
            request = context['request']
            news = self._paginate(request, news, self.paginate_by)

        context[self.name] = news
        return ''

def _get_news(parser, token, tag_name, query_set=None):
    args = token.split_contents()[1:]
    kwargs = {
        'as': None,
        'limit': None,
        'category': None,
        'order_by': None,
        'paginate_by': None,
        'query_set': query_set,
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
            if key in ('limit', 'paginate_by'):
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
    kwargs['name'] = kwargs['as']
    kwargs.pop('as')
    return GetNewsListNode(**kwargs)

@register.tag
def get_all_news(parser, token):
    """
    This will store a list of the news
    in the context.

    Usage::

        {% get_all_news as news %}
        {% get_all_news as news paginate_by 25 %}
        {% get_all_news as news max 5 %}
        {% get_all_news as news category 'main'  %}
        {% get_all_news as news order_by '-date'  %}

        {% for item in news %}
        ...
        {% endfor %}
    """
    return _get_news(parser, token, 'get_all_news', models.News.objects.all)

@register.tag
def get_published_news(parser, token):
    """
    This will store a list of the news
    in the context.

    Usage::

        {% get_published_news as news %}
        {% get_published_news as news paginate_by 25 %}
        {% get_published_news as news max 5 %}
        {% get_published_news as news category 'main'  %}
        {% get_published_news as news order_by '-date'  %}

        {% for item in news %}
        ...
        {% endfor %}
    """
    return _get_news(parser, token, 'get_published_news', models.News.objects.published)

@register.tag
def get_draft_news(parser, token):
    """
    This will store a list of the news
    in the context.

    Usage::

        {% get_draft_news as news %}
        {% get_draft_news as news paginate_by 25 %}
        {% get_draft_news as news max 5 %}
        {% get_draft_news as news category 'main'  %}
        {% get_draft_news as news order_by '-date'  %}

        {% for item in news %}
        ...
        {% endfor %}
    """
    return _get_news(parser, token, 'get_draft_news', models.News.objects.draft)

class GetNewsNode(template.Node):
    def __init__(self, name):
        self.name = name

    def render(self, context):
        request = context['request']
        slug = context['params']['slug']
        try:
            news = models.NewsTranslation.objects.get(slug=slug).news
        except models.NewsTranslation.DoesNotExist:
            news = models.News.objects.get(slug=slug)
        context[self.name] = news

        return ''

@register.tag
def get_news(parser, token):
    """
    Usage::

        {% get_news as news %}
    """
    args = token.split_contents()
    if len(args) < 3:
        raise TemplateSyntaxError, "'get_news' requires 'as variable' (got %r)" % args
    return GetNewsNode(args[2])

