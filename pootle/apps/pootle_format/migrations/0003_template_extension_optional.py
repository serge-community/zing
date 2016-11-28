# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pootle_format', '0002_default_formats'),
    ]

    operations = [
        migrations.AlterField(
            model_name='format',
            name='template_extension',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='template_formats', to='pootle_format.FileExtension'),
        ),
    ]
