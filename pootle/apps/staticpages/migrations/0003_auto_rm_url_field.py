# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("staticpages", "0002_change_url_field_help_text"),
    ]

    operations = [
        migrations.RemoveField(model_name="legalpage", name="url",),
        migrations.RemoveField(model_name="staticpage", name="url",),
    ]
