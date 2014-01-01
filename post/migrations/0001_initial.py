# -*- coding: utf-8 -*-

# Copyright (C) 2007-2014, Raffaele Salmaso <raffaele@salmaso.org>
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
from django.conf import settings

user_model = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')

class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Category'
        db.create_table(u'post_category', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('status', self.gf('fluo.models.fields.StatusField')()),
            ('ordering', self.gf('fluo.models.fields.OrderField')(default=0, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('default', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'post', ['Category'])

        # Adding model 'Post'
        db.create_table(u'post_post', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ordering', self.gf('fluo.models.fields.OrderField')(default=0, blank=True)),
            ('created_at', self.gf('fluo.models.fields.CreationDateTimeField')(default=datetime.datetime.now, blank=True)),
            ('last_modified_at', self.gf('fluo.models.fields.ModificationDateTimeField')(default=datetime.datetime.now, blank=True)),
            ('uuid', self.gf('django.db.models.fields.CharField')(max_length=36, null=True, blank=True)),
            ('status', self.gf('fluo.models.fields.StatusField')(default='draft')),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'post-post-owned', null=True, to=orm[user_model])),
            ('event_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('pub_date_begin', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('pub_date_end', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=255)),
            ('abstract', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('note', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'post', ['Post'])

        # Adding M2M table for field users on 'Post'
        m2m_table_name = db.shorten_name(u'post_post_users')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('post', models.ForeignKey(orm[u'post.post'], null=False)),
            ('user', models.ForeignKey(orm[u'accounts.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['post_id', 'user_id'])

        # Adding M2M table for field categories on 'Post'
        m2m_table_name = db.shorten_name(u'post_post_categories')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('post', models.ForeignKey(orm[u'post.post'], null=False)),
            ('category', models.ForeignKey(orm[u'post.category'], null=False))
        ))
        db.create_unique(m2m_table_name, ['post_id', 'category_id'])

        # Adding model 'PostTranslation'
        db.create_table(u'post_posttranslation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=5, db_index=True)),
            ('title', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=255)),
            ('abstract', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', to=orm['post.Post'])),
        ))
        db.send_create_signal(u'post', ['PostTranslation'])

        # Adding unique constraint on 'PostTranslation', fields ['parent', 'language']
        db.create_unique(u'post_posttranslation', ['parent_id', 'language'])

        # Adding unique constraint on 'PostTranslation', fields ['title', 'slug']
        db.create_unique(u'post_posttranslation', ['title', 'slug'])


    def backwards(self, orm):
        # Removing unique constraint on 'PostTranslation', fields ['title', 'slug']
        db.delete_unique(u'post_posttranslation', ['title', 'slug'])

        # Removing unique constraint on 'PostTranslation', fields ['parent', 'language']
        db.delete_unique(u'post_posttranslation', ['parent_id', 'language'])

        # Deleting model 'Category'
        db.delete_table(u'post_category')

        # Deleting model 'Post'
        db.delete_table(u'post_post')

        # Removing M2M table for field users on 'Post'
        db.delete_table(db.shorten_name(u'post_post_users'))

        # Removing M2M table for field categories on 'Post'
        db.delete_table(db.shorten_name(u'post_post_categories'))

        # Deleting model 'PostTranslation'
        db.delete_table(u'post_posttranslation')


    models = {
        user_model: {
            'Meta': {'object_name': user_model.split('.')[1]},
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
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'locations.administrativearea1': {
            'Meta': {'object_name': 'AdministrativeArea1'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'long_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'locations.administrativearea2': {
            'Meta': {'object_name': 'AdministrativeArea2'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'long_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'locations.administrativearea3': {
            'Meta': {'object_name': 'AdministrativeArea3'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'long_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'locations.country': {
            'Meta': {'object_name': 'Country'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'long_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'locations.locality': {
            'Meta': {'object_name': 'Locality'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'long_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'locations.location': {
            'Meta': {'object_name': 'Location'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'administrative_area_level_1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'locations'", 'null': 'True', 'to': u"orm['locations.AdministrativeArea1']"}),
            'administrative_area_level_2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'locations'", 'null': 'True', 'to': u"orm['locations.AdministrativeArea2']"}),
            'administrative_area_level_3': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'locations'", 'null': 'True', 'to': u"orm['locations.AdministrativeArea3']"}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'locations'", 'null': 'True', 'to': u"orm['locations.Country']"}),
            'dump': ('django.db.models.fields.TextField', [], {}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'geo_lat': ('django.db.models.fields.DecimalField', [], {'max_digits': '13', 'decimal_places': '10'}),
            'geo_lng': ('django.db.models.fields.DecimalField', [], {'max_digits': '13', 'decimal_places': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locality': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'locations'", 'null': 'True', 'to': u"orm['locations.Locality']"}),
            'other_info': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'locations'", 'to': u"orm[user_model]"}),
            'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True'}),
            'route': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'telephone_no': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        u'post.category': {
            'Meta': {'object_name': 'Category'},
            'default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'ordering': ('fluo.models.fields.OrderField', [], {'default': '0', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'status': ('fluo.models.fields.StatusField', [], {})
        },
        u'post.post': {
            'Meta': {'object_name': 'Post'},
            'abstract': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'post'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['post.Category']"}),
            'created_at': ('fluo.models.fields.CreationDateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'event_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_at': ('fluo.models.fields.ModificationDateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'ordering': ('fluo.models.fields.OrderField', [], {'default': '0', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'post-post-owned'", 'null': 'True', 'to': u"orm[user_model]"}),
            'pub_date_begin': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'pub_date_end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255'}),
            'status': ('fluo.models.fields.StatusField', [], {'default': "'draft'"}),
            'text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'post-post-visible'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm[user_model]"}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'})
        },
        u'post.posttranslation': {
            'Meta': {'unique_together': "(('parent', 'language'), ('title', 'slug'))", 'object_name': 'PostTranslation'},
            'abstract': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '5', 'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'to': u"orm['post.Post']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        }
    }

    complete_apps = ['post']
