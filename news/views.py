# -*- coding: utf-8 -*-

# Copyright (C) 2007-2009, Salmaso Raffaele <raffaele@salmaso.org>
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

from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.conf import settings
from django.shortcuts import get_object_or_404
from fluo.shortcuts import render_to_response
from news.models import News, NewsTranslation

def news_list(request, template_name='news/list.html', paginate_by=25):
    news_list = News.objects.published()
    paginate_by = getattr(settings, 'NEWS_PAGINATE_BY', paginate_by)
    paginator = Paginator(news_list, paginate_by)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        news = paginator.page(page)
    except (EmptyPage, InvalidPage):
        news = paginator.page(paginator.num_pages)

    return render_to_response(
        template_name,
        request=request,
        news=news,
    )

def news_detail(request, slug, template_name='news/detail.html'):
    try:
        news = NewsTranslation.objects.get(slug=slug).news
    except NewsTranslation.DoesNotExist:
        news = get_object_or_404(News, slug=slug)
    return render_to_response(
        template_name,
        request=request,
        news=news,
    )

