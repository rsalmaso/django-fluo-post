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

from south.db import db
from fluo import models
from news.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Category'
        db.create_table('news_category', (
            ('id', orm['news.Category:id']),
            ('status', orm['news.Category:status']),
            ('ordering', orm['news.Category:ordering']),
            ('name', orm['news.Category:name']),
            ('slug', orm['news.Category:slug']),
            ('default', orm['news.Category:default']),
        ))
        db.send_create_signal('news', ['Category'])
        
        # Adding model 'News'
        db.create_table('news_news', (
            ('id', orm['news.News:id']),
            ('ordering', orm['news.News:ordering']),
            ('status', orm['news.News:status']),
            ('event_date', orm['news.News:event_date']),
            ('pub_date_begin', orm['news.News:pub_date_begin']),
            ('pub_date_end', orm['news.News:pub_date_end']),
            ('title', orm['news.News:title']),
            ('slug', orm['news.News:slug']),
            ('abstract', orm['news.News:abstract']),
            ('text', orm['news.News:text']),
            ('note', orm['news.News:note']),
        ))
        db.send_create_signal('news', ['News'])
        
        # Adding model 'NewsTranslation'
        db.create_table('news_newstranslation', (
            ('id', orm['news.NewsTranslation:id']),
            ('language', orm['news.NewsTranslation:language']),
            ('news', orm['news.NewsTranslation:news']),
            ('title', orm['news.NewsTranslation:title']),
            ('slug', orm['news.NewsTranslation:slug']),
            ('abstract', orm['news.NewsTranslation:abstract']),
            ('text', orm['news.NewsTranslation:text']),
        ))
        db.send_create_signal('news', ['NewsTranslation'])
        
        # Creating unique_together for [news, language] on NewsTranslation.
        db.create_unique('news_newstranslation', ['news_id', 'language'])
        
        # Creating unique_together for [title, slug] on News.
        db.create_unique('news_news', ['title', 'slug'])
        
        # Creating unique_together for [title, slug] on NewsTranslation.
        db.create_unique('news_newstranslation', ['title', 'slug'])
        
    
    
    def backwards(self, orm):
        
        # Deleting unique_together for [title, slug] on NewsTranslation.
        db.delete_unique('news_newstranslation', ['title', 'slug'])
        
        # Deleting unique_together for [title, slug] on News.
        db.delete_unique('news_news', ['title', 'slug'])
        
        # Deleting unique_together for [news, language] on NewsTranslation.
        db.delete_unique('news_newstranslation', ['news_id', 'language'])
        
        # Deleting model 'Category'
        db.delete_table('news_category')
        
        # Deleting model 'News'
        db.delete_table('news_news')
        
        # Deleting model 'NewsTranslation'
        db.delete_table('news_newstranslation')
        
    
    
    models = {
        'auth.group': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)"},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'news.category': {
            'default': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '25'}),
            'ordering': ('models.OrderField', [], {'default': '0'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'status': ('models.StatusField', [], {})
        },
        'news.news': {
            'Meta': {'unique_together': "(('title', 'slug'),)"},
            'abstract': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['news.Category']", 'null': 'True', 'blank': 'True'}),
            'event_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'ordering': ('models.OrderField', [], {'default': '0'}),
            'pub_date_begin': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'pub_date_end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'status': ('models.StatusField', [], {}),
            'text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'news.newstranslation': {
            'Meta': {'unique_together': "(('news', 'language'), ('title', 'slug'))"},
            'abstract': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '5', 'db_index': 'True'}),
            'news': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'to': "orm['news.News']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        }
    }
    
    complete_apps = ['news']
