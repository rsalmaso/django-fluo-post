# -*- coding: utf-8 -*-

# Copyright (C) 2007-2011, Raffaele Salmaso <raffaele@salmaso.org>
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
from post import models

register = template.Library()

class GetPostListNode(template.Node):
    def __init__(self, name, category=None, order_by=None, limit=None, query_set=None, paginate_by=False):
        self.name = name
        self.limit = limit
        self.query_set = query_set
        self.category = category
        self.order_by = order_by
        self.paginate_by = paginate_by

    def _paginate(self, request, news_list, paginate_by):
        paginator = Paginator(post_list, paginate_by)

        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1

        try:
            post = paginator.page(page)
        except (EmptyPage, InvalidPage):
            post = paginator.page(paginator.num_pages)

        return post

    def render(self, context):
        post = self.query_set()

        if self.category:
            post = post.filter(categories__name__in=self.category)

        if self.order_by:
            post = post.order_by(*self.order_by)

        if self.limit:
            post = post[:self.limit]

        if self.paginate_by:
            request = context['request']
            post = self._paginate(request, post, self.paginate_by)

        context[self.name] = post
        return ''

def _get_post(parser, token, tag_name, query_set=None):
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
    return GetPostListNode(**kwargs)

@register.tag
def get_all_post(parser, token, name='get_all_post', post_model=models.Post, translation_model=models.PostTranslation):
    """
    This will store a list of the post
    in the context.

    Usage::

        {% get_all_post as post %}
        {% get_all_post as post paginate_by 25 %}
        {% get_all_post as post limit 5 %}
        {% get_all_post as post category 'main'  %}
        {% get_all_post as post order_by '-date'  %}

        {% for item in post %}
        ...
        {% endfor %}
    """
    return _get_post(parser, token, name, post_model.objects.all)

@register.tag
def get_published_post(parser, token, name='get_published_post', post_model=models.Post, translation_model=models.PostTranslation):
    """
    This will store a list of the post
    in the context.

    Usage::

        {% get_published_post as post %}
        {% get_published_post as post paginate_by 25 %}
        {% get_published_post as post limit 5 %}
        {% get_published_post as post category 'main'  %}
        {% get_published_post as post order_by '-date'  %}

        {% for item in post %}
        ...
        {% endfor %}
    """
    return _get_post(parser, token, name, post_model.objects.published)

@register.tag
def get_draft_post(parser, token, name='get_draft_post', post_model=models.Post, translation_model=models.PostTranslation):
    """
    This will store a list of the post
    in the context.

    Usage::

        {% get_draft_post as post %}
        {% get_draft_post as post paginate_by 25 %}
        {% get_draft_post as post limit 5 %}
        {% get_draft_post as post category 'main'  %}
        {% get_draft_post as post order_by '-date'  %}

        {% for item in post %}
        ...
        {% endfor %}
    """
    return _get_post(parser, token, name, post_model.objects.draft)

class GetPostNode(template.Node):
    def __init__(self, name, post_model, translation_model):
        self.name = name

    def render(self, context):
        request = context['request']
        slug = context['params']['slug']
        if translation_model is not None:
            try:
                post = translation_model.objects.get(slug=slug).post
            except translation_model.DoesNotExist:
                post = post_model.objects.get(slug=slug)
        else:
            post = post_model.objects.get(slug=slug)
        context[self.name] = post

        return ''

@register.tag
def get_post(parser, token, name='get_post', post_model=models.Post, translation_model=models.PostTranslation):
    """
    Usage::

        {% get_post as post %}
    """
    args = token.split_contents()
    if len(args) < 3:
        raise TemplateSyntaxError, "'%(name)s' requires 'as variable' (got %(args)r)" % {'name': name, 'args': args }
    return GetPostNode(name=args[2], post_model=post_model, translation_model=translation_model)

class GetCalendarNode(template.Node):
    def __init__(self, month, year, var_name):
        self.year = template.Variable(year)
        self.month = template.Variable(month)
        self.var_name = var_name

    def render(self, context):
        mycal = Calendar()
        context[self.var_name] = mycal.monthdatescalendar(int(self.year.resolve(context)), int(self.month.resolve(context)))

        return ''

@register.tag
def get_post_calendar(parser, token, name='get_post_calendar', post_model=models.Post, translation_model=models.PostTranslation):
    syntax_help = "syntax should be \"get_calendar for <month> <year> as <var_name>\""
    # This version uses a regular expression to parse tag contents.
    try:
        # Splitting by None == splitting by spaces.
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires arguments, %s" % (token.contents.split()[0], syntax_help)
    m = re.search(r'for (.*?) (.*?) as (\w+)', arg)
    if m:
        month, year, var = m.groups(0)[0], m.groups(0)[1], m.groups(0)[2]
    else:
        m = re.search(r'as (\w+)', arg)
        if m:
            today = datetime.date.today()
            month = today.month
            year = today.year
            var = m.groups(0)[0]
        else:
            raise template.TemplateSyntaxError, "%r tag had invalid arguments, %s" % (tag_name, syntax_help)

    return GetCalendarNode(month=month, year=year, var_name=var)

