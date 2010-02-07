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
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from fluo.models import Q
from fluo import models

class Category(models.CategoryModel):
    class Meta:
        verbose_name = _('News type')
        verbose_name_plural = _('News types')

DRAFT = 'draft'
PUBLISHED = 'published'

STATUS_CHOICES = (
    (DRAFT, _('Draft')),
    (PUBLISHED, _('Published')),
)

class NewsManager(models.Manager):
    def draft(self):
        return self._filter(status=DRAFT)
    def published(self):
        return self._filter(status=PUBLISHED)
    def _filter(self, status):
        now = datetime.datetime.now()
        q1 = Q(Q(pub_date_begin__isnull=True)|Q(pub_date_begin__lte=now))
        q2 = Q(Q(pub_date_end__isnull=True)|Q(pub_date_end__gte=now))
        return self.filter(status=status).filter(q1 & q2)

class News(models.OrderedModel, models.I18NModel):
    objects = NewsManager()

    status = models.StatusField(
        choices=STATUS_CHOICES,
        help_text=_('If should be displayed or not.'),
    )
    categories = models.ManyToManyField(
        Category,
        null=True,
        blank=True,
        related_name="news",
        verbose_name=_('Categories')
    )
    users = models.ManyToManyField(
        User,
        blank=True,
        null=True,
        related_name='news',
        verbose_name=_('Visible only to'),
        help_text=_('News visible to these users, if empty is visible to all users.'),
    )
    event_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('News date'),
        help_text=_('Date which news refers to.'),
    )
    pub_date_begin = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Publication date begin'),
        help_text=_('When news publication date begins.'),
    )
    pub_date_end = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Publication date end'),
        help_text=_('When news publication date ends.'),
    )
    title = models.CharField(
        unique=True,
        max_length=255,
        verbose_name=_('Title'),
    )
    slug = models.SlugField(
        unique=True,
        max_length=255,
        verbose_name=_('Slug field'),
    )
    abstract = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('Abstract'),
        help_text=_('A brief description of the news'),
    )
    text = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Default text'),
    )
    note = models.TextField(
        blank=True,
        verbose_name=_('Note'),
    )

    class Meta:
        verbose_name = _("News")
        verbose_name_plural = _("News")
        unique_together = (('title', 'slug',),)

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        now = datetime.datetime.now()
        if not self.event_date and self.status == PUBLISHED:
            self.event_date = now
        if not self.pub_date_begin and self.status == PUBLISHED:
            self.pub_date_begin = now
        super(News, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return ('news-detail', (), {'slug': self.translate().slug})

class NewsTranslation(models.TranslationModel):
    news = models.ForeignKey(
        News,
        related_name='translations',
        verbose_name=_('News type'),
    )
    title = models.CharField(
        unique=True,
        max_length=255,
        verbose_name=_('Title'),
    )
    slug = models.SlugField(
        unique=True,
        max_length=255,
        verbose_name=_('Slug field'),
    )
    abstract = models.CharField(
        max_length=255,
        verbose_name=_('Abstract'),
        help_text=_('A brief description'),
    )
    text = models.TextField(
        verbose_name=_('Body'),
    )

    class Meta:
        verbose_name = _("News translation")
        verbose_name_plural = _("News translations")
        unique_together = (('news', 'language',), ('title', 'slug',))

    def __unicode__(self):
        return u'%s (%s)' % (self.news, self.language)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(NewsTranslation, self).save(*args, **kwargs)

