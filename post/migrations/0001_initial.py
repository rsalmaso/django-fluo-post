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

import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Category'
        db.create_table('post_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('status', self.gf('fluo.models.fields.StatusField')()),
            ('ordering', self.gf('fluo.models.fields.OrderField')(default=0, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('default', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('post', ['Category'])

        # Adding model 'Post'
        db.create_table('post_post', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ordering', self.gf('fluo.models.fields.OrderField')(default=0, blank=True)),
            ('created_at', self.gf('fluo.models.fields.CreationDateTimeField')(default=datetime.datetime.now, blank=True)),
            ('last_modified_at', self.gf('fluo.models.fields.ModificationDateTimeField')(default=datetime.datetime.now, blank=True)),
            ('status', self.gf('fluo.models.fields.StatusField')(default='draft')),
            ('event_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('pub_date_begin', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('pub_date_end', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=255)),
            ('abstract', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('note', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('post', ['Post'])

        # Adding M2M table for field users on 'Post'
        db.create_table('post_post_users', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('post', models.ForeignKey(orm['post.post'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('post_post_users', ['post_id', 'user_id'])

        # Adding M2M table for field categories on 'Post'
        db.create_table('post_post_categories', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('post', models.ForeignKey(orm['post.post'], null=False)),
            ('category', models.ForeignKey(orm['post.category'], null=False))
        ))
        db.create_unique('post_post_categories', ['post_id', 'category_id'])

        # Adding model 'PostTranslation'
        db.create_table('post_posttranslation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=5, db_index=True)),
            ('title', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=255)),
            ('abstract', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', to=orm['post.Post'])),
        ))
        db.send_create_signal('post', ['PostTranslation'])

        # Adding unique constraint on 'PostTranslation', fields ['parent', 'language']
        db.create_unique('post_posttranslation', ['parent_id', 'language'])

        # Adding unique constraint on 'PostTranslation', fields ['title', 'slug']
        db.create_unique('post_posttranslation', ['title', 'slug'])

    def backwards(self, orm):
        # Removing unique constraint on 'PostTranslation', fields ['title', 'slug']
        db.delete_unique('post_posttranslation', ['title', 'slug'])

        # Removing unique constraint on 'PostTranslation', fields ['parent', 'language']
        db.delete_unique('post_posttranslation', ['parent_id', 'language'])

        # Deleting model 'Category'
        db.delete_table('post_category')

        # Deleting model 'Post'
        db.delete_table('post_post')

        # Removing M2M table for field users on 'Post'
        db.delete_table('post_post_users')

        # Removing M2M table for field categories on 'Post'
        db.delete_table('post_post_categories')

        # Deleting model 'PostTranslation'
        db.delete_table('post_posttranslation')

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'post.category': {
            'Meta': {'object_name': 'Category'},
            'default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'ordering': ('fluo.models.fields.OrderField', [], {'default': '0', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'status': ('fluo.models.fields.StatusField', [], {})
        },
        'post.post': {
            'Meta': {'object_name': 'Post'},
            'abstract': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'post'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['post.Category']"}),
            'created_at': ('fluo.models.fields.CreationDateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'event_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_at': ('fluo.models.fields.ModificationDateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'ordering': ('fluo.models.fields.OrderField', [], {'default': '0', 'blank': 'True'}),
            'pub_date_begin': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'pub_date_end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255'}),
            'status': ('fluo.models.fields.StatusField', [], {'default': "'draft'"}),
            'text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'post-post-post'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['auth.User']"})
        },
        'post.posttranslation': {
            'Meta': {'unique_together': "(('parent', 'language'), ('title', 'slug'))", 'object_name': 'PostTranslation'},
            'abstract': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '5', 'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'to': "orm['post.Post']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        }
    }

    complete_apps = ['post']
