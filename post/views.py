# Copyright (C) 2007-2016, Raffaele Salmaso <raffaele@salmaso.org>
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

from django.db.models import Q
from django.conf import settings
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import Http404
from django.shortcuts import render
from django.views.generic import View


class PostView(View):
    def process_context(self, request, context=None):
        context = {} if context is None else context
        return context


class ListView(PostView):
    paginate_by = 25
    order_by = None
    post_model = None
    translation_model = None
    template_name = "post/list.html"
    object_list_name = "post_list"

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
            page = int(request.GET.get("page", "1"))
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
    template_name = "post/detail.html"
    object_name = "post"

    def get_object(self, request, slug):
        q = Q(slug__iexact=slug)
        if self.translation_model is not None:
            q |= Q(translations__slug__exact=slug)
        try:
            return self.post_model.objects.published().get(q)
        except self.post_model.DoesNotExist:
            raise Http404

    def get(self, request, slug):
        post = self.get_object(request, slug)

        context = self.process_context(request, {
            self.object_name: post,
        })

        return render(
            request,
            self.template_name,
            context,
        )


if "comments" in settings.INSTALLED_APPS:
    from comments.forms import CommentForm, ModerateForm, HandleForm, Type

    class DetailView(DetailView):
        moderation_form = ModerateForm
        comment_form = CommentForm
        handle_form = HandleForm
        handle_comment = True

        def get_comments(self, request, context):
            raise NotImplemented

        def process_context(self, request, context=None):
            context = super().process_context(request, context)
            if self.handle_comment:
                context["comments"] = self.get_comments(request, context)
                context["form"] = self.comment_form(initial={"type": Type.COMMENT}, user=request.user)
                context["HANDLE"] = Type.HANDLE
                context["MODERATE"] = Type.MODERATE
                context["COMMENT"] = Type.COMMENT
            return context

        def post(self, request, slug, *args, **kwargs):
            post = self.get_object(request, slug)
            context = self.process_context(request, {
                "post": post,
            })
            if self.handle_comment:
                type = request.POST.get("type")
                if type == Type.COMMENT:
                    form = self.comment_form(request.POST, request.user)
                    if form.is_valid():
                        form.save(request, post)
                    else:
                        context["form"] = form
                elif type == Type.MODERATE:
                    form = self.moderation_form(request.POST)
                    if form.is_valid():
                        form.save(request, post)
                elif type == Type.HANDLE:
                    form = self.handle_form(request.POST)
                    if form.is_valid():
                        form.save(request, post)
            return render(
                request,
                self.template_name,
                context,
            )


class PreviewView(DetailView):
    def get(self, request, slug):
        token = request.GET.get("token", None)

        if not token:
            raise Http404

        return super().get(request, slug)
