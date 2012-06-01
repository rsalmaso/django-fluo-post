# -*- coding: utf-8 -*-

# Copyright (C) 2007-2012, Salmaso Raffaele <raffaele@salmaso.org>
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

from django.http import Http404
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.shortcuts import get_object_or_404, render
from fluo.views import View
from post.models import Post, PostTranslation, PUBLISHED

class ListView(View):
    paginate_by = 25
    order_by = None
    post_model = Post
    translation_model = PostTranslation
    template_name = 'post/list.html'

    def get(self, request):
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

        return render(
            request,
            self.template_name,
            { 'post': post },
        )

class DetailView(View):
    post_model = Post
    translation_model = PostTranslation
    template_name = 'post/detail.html'

    def get(self, request, slug):
        if self.translation_model is not None:
            try:
                post = self.translation_model.objects.get(slug=slug, parent__status=PUBLISHED).parent
            except self.translation_model.DoesNotExist:
                post = get_object_or_404(self.post_model, slug=slug, status=PUBLISHED)
        else:
            post = get_object_or_404(self.post_model, slug=slug, status=PUBLISHED)
        return render(
            request,
            self.template_name,
            { 'post': post },
        )

class PreviewView(View):
    post_model = Post
    translation_model = PostTranslation
    template_name = 'post/detail.html'

    def get(self, request, slug):
        token = request.GET.get('token', None)

        if not token:
            raise Http404

        if self.translation_model is not None:
            try:
                post = self.translation_model.objects.get(slug=slug, uuid=token).parent
            except self.translation_model.DoesNotExist:
                post = get_object_or_404(self.post_model, slug=slug, uuid=token)
        else:
            post = get_object_or_404(self.post_model, slug=slug, uuid=token)
        return render(
            request,
            self.template_name,
            { 'post': post },
        )

