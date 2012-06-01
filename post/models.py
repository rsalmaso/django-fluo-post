# -*- coding: utf-8 -*-

# Copyright (C) 2007-2012, Raffaele Salmaso <raffaele@salmaso.org>
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
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from fluo.models import Q
from fluo import models

DRAFT = 'draft'
PUBLISHED = 'published'

STATUS_CHOICES = (
    (DRAFT, _('Draft')),
    (PUBLISHED, _('Published')),
)

class PostManager(models.Manager):
    def draft(self):
        return self._filter(status=DRAFT)
    def published(self):
        return self._filter(status=PUBLISHED)
    def _filter(self, status):
        now = timezone.now()
        q1 = Q(Q(pub_date_begin__isnull=True)|Q(pub_date_begin__lte=now))
        q2 = Q(Q(pub_date_end__isnull=True)|Q(pub_date_end__gte=now))
        return self.filter(status=status).filter(q1 & q2)

class PostBase(models.TimestampModel, models.OrderedModel, models.I18NModel):
    objects = PostManager()

    status = models.StatusField(
        choices=STATUS_CHOICES,
        default=DRAFT,
        help_text=_('If should be displayed or not.'),
    )
    owner = models.ForeignKey(
        User,
        blank=True,
        null=True,
        related_name='%(app_label)s-%(class)s-owned',
        verbose_name=_('owned by'),
        help_text=_('Post owner.'),
    )
    users = models.ManyToManyField(
        User,
        blank=True,
        null=True,
        related_name='%(app_label)s-%(class)s-visible',
        verbose_name=_('Visible only to'),
        help_text=_('Post visible to these users, if empty is visible to all users.'),
    )
    event_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Post date'),
        help_text=_('Date which post refers to.'),
    )
    pub_date_begin = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Publication date begin'),
        help_text=_('When post publication date begins.'),
    )
    pub_date_end = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Publication date end'),
        help_text=_('When post publication date ends.'),
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
        help_text=_('A brief description of the post'),
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
        abstract = True
        unique_together = (('title', 'slug',),)

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        now = timezone.now()
        if not self.event_date and self.status == PUBLISHED:
            self.event_date = now
        if not self.pub_date_begin and self.status == PUBLISHED:
            self.pub_date_begin = now
        super(PostBase, self).save(*args, **kwargs)

class PostBaseTranslation(models.TranslationModel):
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
        abstract = True

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(PostBaseTranslation, self).save(*args, **kwargs)

class Category(models.CategoryModel):
    class Meta:
        verbose_name = _('Post type')
        verbose_name_plural = _('Post types')

class Post(PostBase):
    categories = models.ManyToManyField(
        Category,
        null=True,
        blank=True,
        related_name="post",
        verbose_name=_('Categories')
    )

    class Meta:
        verbose_name = _("Post")
        verbose_name_plural = _("Post")

    @models.permalink
    def get_absolute_url(self):
        return ('post-detail', (), {'slug': self.translate().slug})

class PostTranslation(PostBaseTranslation):
    parent = models.ForeignKey(
        Post,
        related_name='translations',
        verbose_name=_('Post type'),
    )

    class Meta:
        verbose_name = _("Post translation")
        verbose_name_plural = _("Post translations")
        unique_together = (('parent', 'language',), ('title', 'slug',))

    def __unicode__(self):
        return u'%s (%s)' % (self.parent, self.language)

