# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import pootle.models.duedate


class Migration(migrations.Migration):

    dependencies = [
        ("pootle", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="duedate",
            name="pootle_path",
            field=models.CharField(
                db_index=True,
                max_length=255,
                unique=True,
                validators=[pootle.models.duedate.validate_pootle_path],
            ),
        ),
    ]
