# -*- coding: utf-8 -*-

# Copyright (C) 2007-2011, Salmaso Raffaele <raffaele@salmaso.org>
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
from post.models import Post, PostTranslation
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required

class PostView(object):
    prefix = 'post'
    paginate_by = 25
    order_by = None
    post_model = Post
    translation_model = PostTranslation

    def __init__(self):
        self.list_template_name = '%s/list.html' % self.prefix
        self.detail_template_name = '%s/detail.html' % self.prefix

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url, include

        urlpatterns = patterns('',
            url(r'^$', self.list_view, name='%s-list' % self.prefix),
            url(r'^(?P<slug>.*)/$', self.detail_view, name='%s-detail' % self.prefix),
        )
        return urlpatterns

    def urls(self):
        return self.get_urls()
    urls = property(urls)

    def list_view(self, request):
        post_list = self.post_model.objects.published()
        if self.order_by:
            post_list = post_list.order_by(*self.order_by)
        paginator = Paginator(post_list, self.paginate_by)

        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1

        try:
            post = paginator.page(page)
        except (EmptyPage, InvalidPage):
            post = paginator.page(paginator.num_pages)

        return render_to_response(
            self.list_template_name,
            request=request,
            post=post,
        )

    def detail_view(self, request, slug):
        if self.translation_model is not None:
            try:
                post = self.translation_model.objects.get(slug=slug).post
            except self.translation_model.DoesNotExist:
                post = get_object_or_404(self.post_model, slug=slug)
        else:
            post = get_object_or_404(self.post_model, slug=slug)
        return render_to_response(
            self.detail_template_name,
            request=request,
            post=post,
        )

