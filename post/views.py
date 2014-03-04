# -*- coding: utf-8 -*-

# Copyright (C) 2007-2014, Salmaso Raffaele <raffaele@salmaso.org>
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

from __future__ import unicode_literals
from django.http import Http404
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.shortcuts import get_object_or_404, render
from fluo.views import View
from .models import PUBLISHED


class PostView(View):
    def process_context(self, request, context=None):
        context = {} if context is None else context
        return context


class ListView(PostView):
    paginate_by = 25
    order_by = None
    post_model = None
    translation_model = None
    template_name = 'post/list.html'
    object_list_name = 'post_list'

    def get_queryset(self, request):
        return self.post_model.objects.published()

    def get(self, request):
        object_list = self.get_queryset(request)
        if self.order_by:
            object_list = object_list.order_by(*self.order_by)
        paginator = Paginator(object_list, self.paginate_by)

        context = self.process_context(request, {
            self.object_list_name: object_list,
        })

        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1

        try:
            post_list = paginator.page(page)
        except (EmptyPage, InvalidPage):
            post_list = paginator.page(paginator.num_pages)

        context[self.object_list_name] = post_list

        return render(
            request,
            self.template_name,
            context,
        )


class DetailView(PostView):
    post_model = None
    translation_model = None
    template_name = 'post/detail.html'
    object_name = 'post'

    def get_post(self, request, slug):
        if self.translation_model is not None:
            try:
                post = self.translation_model.objects.get(slug=slug, parent__status=PUBLISHED).parent
            except self.translation_model.DoesNotExist:
                post = get_object_or_404(self.post_model, slug=slug, status=PUBLISHED)
        else:
            post = get_object_or_404(self.post_model, slug=slug, status=PUBLISHED)
        return post

    def get(self, request, slug):
        post = self.get_post(request, slug)

        context = self.process_context(request, {
            self.object_name: post,
        })

        return render(
            request,
            self.template_name,
            context,
        )


class PreviewView(DetailView):
    def get(self, request, slug):
        token = request.GET.get('token', None)

        if not token:
            raise Http404

        return super(PreviewView, self).get(request, slug)
