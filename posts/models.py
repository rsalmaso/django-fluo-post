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

from uuid import uuid1
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.template.defaultfilters import slugify
from fluo.db.models import Q
from fluo.db import models


class PostModelQuerySet(models.QuerySet):
    def draft(self):
        return self._filter(status=PostModel.STATUS_DRAFT)

    def published(self):
        return self._filter(status=PostModel.STATUS_PUBLISHED)

    def first(self, **kwargs):
        try:
            return self.filter(**kwargs).order_by("pub_date_begin")[0]
        except (self.model.DoesNotExist, IndexError):
            raise self.model.DoesNotExist

    def last(self, **kwargs):
        try:
            return self.filter(**kwargs).order_by("-pub_date_begin")[0]
        except (self.model.DoesNotExist, IndexError):
            raise self.model.DoesNotExist

    def _filter(self, status):
        now = timezone.now()
        q1 = Q(Q(pub_date_begin__isnull=True)|Q(pub_date_begin__lte=now))
        q2 = Q(Q(pub_date_end__isnull=True)|Q(pub_date_end__gte=now))
        return self.filter(status=status).filter(q1 & q2)


class PostModelManager(models.Manager.from_queryset(PostModelQuerySet)):
    use_for_related_fields = True
    silence_use_for_related_fields_deprecation = True


class PostModel(models.TimestampModel, models.OrderedModel, models.I18NModel):
    STATUS_DRAFT = "draft"
    STATUS_PUBLISHED = "published"
    STATUS_CHOICES = [
        (STATUS_DRAFT, _("Draft")),
        (STATUS_PUBLISHED, _("Published")),
    ]

    objects = PostModelManager()

    uuid = models.CharField(
        max_length=36,
        blank=True,
        null=True,
        verbose_name=_("uuid field"),
        help_text=_("for preview."),
    )
    status = models.StatusField(
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
        help_text=_("If should be displayed or not."),
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_owned",
        verbose_name=_("owned by"),
        help_text=_("Post owner."),
    )
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="%(app_label)s_%(class)s_visible",
        verbose_name=_("Visible only to"),
        help_text=_("Post visible to these users, if empty is visible to all users."),
    )
    event_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("Post date"),
        help_text=_("Date which post refers to."),
    )
    pub_date_begin = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("Publication date begin"),
        help_text=_("When post publication date begins."),
    )
    pub_date_end = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("Publication date end"),
        help_text=_("When post publication date ends."),
    )
    title = models.CharField(
        unique=True,
        max_length=255,
        verbose_name=_("Title"),
    )
    slug = models.SlugField(
        unique=True,
        max_length=255,
        verbose_name=_("Slug field"),
    )
    abstract = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Abstract"),
        help_text=_("A brief description of the post"),
    )
    text = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Default text"),
    )
    note = models.TextField(
        blank=True,
        verbose_name=_("Note"),
    )

    class Meta:
        abstract = True
        base_manager_name = "objects"
        unique_together = [("title", "slug")]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        now = timezone.now()
        if not self.event_date and self.status == PostModel.STATUS_PUBLISHED:
            self.event_date = now
        if not self.pub_date_begin and self.status == PostModel.STATUS_PUBLISHED:
            self.pub_date_begin = now
        if not self.uuid:
            self.uuid = uuid1()
        super().save(*args, **kwargs)

    @property
    def next(self):
        posts = self._default_manager.filter(status=self.status, pub_date_begin__gt=self.pub_date_begin)
        try:
            post = posts[0]
        except:
            post = None
        return post

    @property
    def prev(self):
        posts = self._default_manager.filter(status=self.status, pub_date_begin__lt=self.pub_date_begin)
        try:
            post = posts[0]
        except:
            post = None
        return post


class PostModelTranslation(models.TranslationModel):
    title = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("Title"),
    )
    slug = models.SlugField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("Slug field"),
    )
    abstract = models.TextField(
        verbose_name=_("Abstract"),
        blank=True,
        null=True,
        help_text=_("A brief description"),
    )
    text = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Body"),
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)


if "comments" in settings.INSTALLED_APPS:
    class PostCommentModel(PostModel):
        can_comment = models.BooleanField(
            default=True,
            verbose_name=_("can comment"),
        )

        class Meta:
            abstract = True
