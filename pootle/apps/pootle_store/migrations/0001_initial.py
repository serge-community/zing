# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

import translate.storage.base

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.utils.timezone import utc

import pootle.core.mixins.treeitem
import pootle.core.storage
import pootle_store.fields
import pootle_store.models
from pootle.core.utils.db import set_mysql_collation_for_column


def make_store_paths_cs(apps, schema_editor):
    cursor = schema_editor.connection.cursor()
    set_mysql_collation_for_column(
        apps,
        cursor,
        'pootle_store.Store',
        'pootle_path',
        'utf8_bin',
        'varchar(255)',
    )
    set_mysql_collation_for_column(
        apps,
        cursor,
        'pootle_store.Store',
        'name',
        'utf8_bin',
        'varchar(255)',
    )


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pootle_app', '0001_initial'),
        # Avoids circular dependency
        # ('pootle_translationproject', '0003_realpath_can_be_none'),
        # ('pootle_project', '0001_initial'),
        # ('pootle_translationproject', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Store',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', pootle_store.fields.TranslationStoreField(db_index=True, editable=False, max_length=255, storage=pootle.core.storage.PootleFileSystemStorage(), upload_to=b'')),
                ('pootle_path', models.CharField(db_index=True, max_length=255, unique=True, verbose_name='Path')),
                ('name', models.CharField(editable=False, max_length=128, validators=[pootle_store.models.validate_no_slashes])),
                ('file_mtime', models.DateTimeField(default=datetime.datetime(1, 1, 1, 0, 0, tzinfo=utc))),
                ('state', models.IntegerField(db_index=True, default=0, editable=False)),
                ('creation_time', models.DateTimeField(auto_now_add=True, db_index=True, null=True)),
                ('last_sync_revision', models.IntegerField(blank=True, db_index=True, null=True)),
                ('obsolete', models.BooleanField(default=False)),
                ('parent', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='child_stores', to='pootle_app.Directory')),
                # ('translation_project', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='stores', to='pootle_translationproject.TranslationProject')),
            ],
            options={
                'ordering': ['pootle_path'],
            },
            bases=(models.Model, pootle.core.mixins.treeitem.CachedTreeItem, translate.storage.base.TranslationStore),
        ),

        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('index', models.IntegerField(db_index=True)),
                ('unitid', models.TextField(editable=False)),
                ('unitid_hash', models.CharField(db_index=True, editable=False, max_length=32)),
                ('source_f', pootle_store.fields.MultiStringField(null=True)),
                ('source_hash', models.CharField(db_index=True, editable=False, max_length=32)),
                ('source_wordcount', models.SmallIntegerField(default=0, editable=False)),
                ('source_length', models.SmallIntegerField(db_index=True, default=0, editable=False)),
                ('target_f', pootle_store.fields.MultiStringField(blank=True, null=True)),
                ('target_wordcount', models.SmallIntegerField(default=0, editable=False)),
                ('target_length', models.SmallIntegerField(db_index=True, default=0, editable=False)),
                ('developer_comment', models.TextField(blank=True, null=True)),
                ('translator_comment', models.TextField(blank=True, null=True)),
                ('locations', models.TextField(editable=False, null=True)),
                ('context', models.TextField(editable=False, null=True)),
                ('state', models.IntegerField(db_index=True, default=0)),
                ('revision', models.IntegerField(blank=True, db_index=True, default=0)),
                ('creation_time', models.DateTimeField(auto_now_add=True, db_index=True, null=True)),
                ('mtime', models.DateTimeField(auto_now=True, db_index=True)),
                ('submitted_on', models.DateTimeField(db_index=True, null=True)),
                ('commented_on', models.DateTimeField(db_index=True, null=True)),
                ('reviewed_on', models.DateTimeField(db_index=True, null=True)),
                ('commented_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='commented', to=settings.AUTH_USER_MODEL)),
                ('reviewed_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reviewed', to=settings.AUTH_USER_MODEL)),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pootle_store.Store')),
                ('submitted_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='submitted', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['store', 'index'],
            },
            bases=(models.Model, translate.storage.base.TranslationUnit),
        ),

        migrations.CreateModel(
            name='Suggestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('target_f', pootle_store.fields.MultiStringField()),
                ('target_hash', models.CharField(db_index=True, max_length=32)),
                ('translator_comment_f', models.TextField(blank=True, null=True)),
                ('state', models.CharField(choices=[(b'pending', 'Pending'), (b'accepted', 'Accepted'), (b'rejected', 'Rejected')], db_index=True, default=b'pending', max_length=16)),
                ('creation_time', models.DateTimeField(db_index=True, null=True)),
                ('review_time', models.DateTimeField(db_index=True, null=True)),
                ('unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pootle_store.Unit')),
                ('reviewer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='suggestions', to=settings.AUTH_USER_MODEL)),
            ],
            bases=(models.Model, translate.storage.base.TranslationUnit),
        ),

        migrations.CreateModel(
            name='QualityCheck',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=64)),
                ('category', models.IntegerField(default=0)),
                ('message', models.TextField()),
                ('false_positive', models.BooleanField(db_index=True, default=False)),
                ('unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pootle_store.Unit')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='store',
            unique_together=set([('parent', 'name')]),
        ),
        migrations.RunPython(
            code=make_store_paths_cs,
        ),
        migrations.AlterUniqueTogether(
            name='unit',
            unique_together=set([('store', 'unitid_hash')]),
        ),
        migrations.AlterIndexTogether(
            name='unit',
            index_together=set([('store', 'revision'), ('store', 'index'), ('store', 'mtime')]),
        ),
        migrations.AlterModelOptions(
            name='unit',
            options={'get_latest_by': 'mtime'},
        ),
    ]
