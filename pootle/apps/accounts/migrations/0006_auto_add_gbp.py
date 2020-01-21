# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_remove_user_unit_rows'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='currency',
            field=models.CharField(blank=True, choices=[('USD', 'USD'), ('EUR', 'EUR'), ('CNY', 'CNY'), ('JPY', 'JPY'), ('GBP', 'GBP')], max_length=3, null=True, verbose_name='Currency'),
        ),
    ]
