# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion

import pootle.core.mixins.treeitem
import pootle_project.models
from pootle.core.utils.db import set_mysql_collation_for_column


def make_project_codes_cs(apps, schema_editor):
    cursor = schema_editor.connection.cursor()
    set_mysql_collation_for_column(
        apps, cursor, "pootle_project.Project", "code", "utf8_bin", "varchar(255)"
    )


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("pootle_language", "0001_initial"),
        ("pootle_store", "0001_initial"),
        ("pootle_app", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Project",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "code",
                    models.CharField(
                        db_index=True,
                        help_text="A short code for the project. This should only contain ASCII characters, numbers, and the underscore (_) character.",
                        max_length=255,
                        unique=True,
                        validators=[pootle_project.models.validate_not_reserved],
                        verbose_name="Code",
                    ),
                ),
                (
                    "fullname",
                    models.CharField(max_length=255, verbose_name="Full Name"),
                ),
                (
                    "checkstyle",
                    models.CharField(
                        choices=[
                            ("creativecommons", "creativecommons"),
                            ("drupal", "drupal"),
                            ("gnome", "gnome"),
                            ("kde", "kde"),
                            ("libreoffice", "libreoffice"),
                            ("mozilla", "mozilla"),
                            ("openoffice", "openoffice"),
                            ("standard", "standard"),
                            ("terminology", "terminology"),
                            ("wx", "wx"),
                        ],
                        default="standard",
                        max_length=50,
                        verbose_name="Quality Checks",
                    ),
                ),
                (
                    "report_email",
                    models.EmailField(
                        blank=True,
                        help_text="An email address where issues with the source text can be reported.",
                        max_length=254,
                        verbose_name="Errors Report Email",
                    ),
                ),
                (
                    "screenshot_search_prefix",
                    models.URLField(
                        blank=True, null=True, verbose_name="Screenshot Search Prefix"
                    ),
                ),
                (
                    "creation_time",
                    models.DateTimeField(auto_now_add=True, db_index=True, null=True),
                ),
                (
                    "disabled",
                    models.BooleanField(default=False, verbose_name="Disabled"),
                ),
                (
                    "directory",
                    models.OneToOneField(
                        editable=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="pootle_app.Directory",
                    ),
                ),
                (
                    "source_language",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="pootle_language.Language",
                        verbose_name="Source Language",
                    ),
                ),
            ],
            options={"ordering": ["code"], "db_table": "pootle_app_project",},
            bases=(
                models.Model,
                pootle.core.mixins.treeitem.CachedTreeItem,
                pootle_project.models.ProjectURLMixin,
            ),
        ),
        migrations.RunPython(code=make_project_codes_cs,),
    ]
