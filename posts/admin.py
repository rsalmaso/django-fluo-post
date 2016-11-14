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

import django
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from fluo import admin
from fluo import forms


MAX_LANGUAGES = len(settings.LANGUAGES)


class PostTranslationInlineModelForm(forms.ModelForm):
    pass
class PostTranslationInlineMixin:
    form = PostTranslationInlineModelForm
    extra = MAX_LANGUAGES
    max_num = MAX_LANGUAGES
    fields = ["language", "title", "abstract", "text"]


class PostAdminForm(forms.ModelForm):
    pass
class PostModelAdmin(admin.OrderedModelAdmin):
    list_display = ["__str__", "status", "event_date", "pub_date_begin", "pub_date_end", "_get_users"]
    list_display_links = ["__str__"]
    list_per_page = 30
    ordering = ["ordering"]
    fieldsets = [
        [None, {"fields": [
            ("status", "ordering",),
            "title",
            "event_date",
            ("pub_date_begin", "pub_date_end",),
            "abstract",
            "text",
            "note",
        ]}],
        [_("Show to"), {"fields": ["users"]}],
    ]

    def _get_users(self, obj):
        users = self.users.all().order_by("username")
        if users:
            return ", ".join([user.username for user in users])
        else:
            return _("All")
    _get_users.short_description = _("Show to")

    def save_model(self, request, obj, form, change):
        is_authenticated = request.user.is_authenticated() if django.VERSION < (1, 10) else request.user.is_authenticated
        if is_authenticated and not obj.owner:
            obj.owner = request.user
        super().save_model(request, obj, form, change)


class PostCommentModelAdmin(PostModelAdmin):
    list_display = ["__str__", "status", "can_comment", "event_date", "pub_date_begin", "pub_date_end", "_get_users"]
    fieldsets = [
        [None, {"fields": [
            ("status", "ordering"),
            "title",
            "event_date",
            ("pub_date_begin", "pub_date_end"),
            "abstract",
            "text",
            "note",
        ]}],
        [_("Show to"), {"fields": ["users"]}],
    ]
