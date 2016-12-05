# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pootle_project', '0012_remove_project_ignoredfiles'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='filetypes',
        ),
    ]
