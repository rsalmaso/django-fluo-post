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

from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from fluo import admin
from fluo import forms
from news.models import News, Category, NewsTranslation

MAX_LANGUAGES = len(settings.LANGUAGES)

class CategoryAdminForm(forms.ModelForm):
    class Meta:
        model = Category
class CategoryAdmin(admin.CategoryModelAdmin):
    model = Category
    form = CategoryAdminForm
admin.site.register(Category, CategoryAdmin)

class NewsTranslationInlineModelForm(forms.ModelForm):
    class Meta:
        model = NewsTranslation
class NewsTranslationInline(admin.TabularInline):
    model = NewsTranslation
    form = NewsTranslationInlineModelForm
    extra = MAX_LANGUAGES
    max_num = MAX_LANGUAGES
    fields = ('language', 'title', 'abstract', 'text',)
class NewsAdminForm(forms.ModelForm):
    class Meta:
        model =  News
class NewsAdmin(admin.OrderedModelAdmin):
    model = News
    form = NewsAdminForm
    list_display = ('__unicode__', 'status', 'event_date', 'pub_date_begin', 'pub_date_end', '_get_categories', '_get_users',)
    list_display_links = ('__unicode__',)
    list_per_page = 30
    ordering = ("ordering",)
    fieldsets = (
        (None, {"fields": (
            ('status', 'ordering',),
            'title',
            'event_date',
            ('pub_date_begin', 'pub_date_end',),
            'abstract',
            'text',
            'note',
        ),}),
        (_('Show to'), {'fields': ('users',),}),
    )
    filter_horizontal = ('users', 'categories',)
    inlines = (NewsTranslationInline,)

    def _get_users(self):
        users = self.users.all().order_by('username')
        if users:
            return u', '.join([user.username for user in users])
        else:
            return _(u'All')
    _get_users.short_description = _('Show to')

    def _get_categories(self):
        categories = self.categories.all().order_by('name')
        if categories:
            return u', '.join([category.name for category in categories])
        else:
            return _(u'All')
    _get_categories.short_description = _('Categories')

admin.site.register(News, NewsAdmin)

