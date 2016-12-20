# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pootle_store', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='translation_project',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='stores', to='pootle_translationproject.TranslationProject')
        ),
    ]
