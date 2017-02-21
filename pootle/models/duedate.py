# -*- coding: utf-8 -*-
#
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.functional import cached_property

from pootle.core.url_helpers import split_pootle_path
from pootle_translationproject.models import TranslationProject


def validate_pootle_path(value):
    project_code = split_pootle_path(value)[1]
    if project_code is None:
        raise ValidationError('Cannot set due date for this path.')


class DueDateManager(models.Manager):

    def for_project(self, project_code):
        """Retrieves a queryset of due dates available for `project_code`."""
        return self.get_queryset().filter(
            pootle_path__regex=r'^/[^/]*/%s/' % project_code
        )


class DueDate(models.Model):

    due_on = models.DateTimeField()
    pootle_path = models.CharField(max_length=255, db_index=True, unique=True,
                                   validators=[validate_pootle_path])
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    modified_on = models.DateTimeField(auto_now_add=True)

    objects = DueDateManager()

    @cached_property
    def path_parts(self):
        return split_pootle_path(self.pootle_path)

    @property
    def language_code(self):
        return self.path_parts[0]

    @property
    def project_code(self):
        return self.path_parts[1]

    def __unicode__(self):
        return u'<DueDate: %s>' % (self.due_on)

    def save(self, *args, **kwargs):
        self.full_clean()

        super(DueDate, self).save(*args, **kwargs)

        if self.language_code is not None:
            return

        # The due date refers to a project: propagate changes to TPs
        existing_due_dates = DueDate.objects.for_project(self.project_code)
        existing_due_dates.update(
            due_on=self.due_on,
            modified_by=self.modified_by,
            modified_on=self.modified_on,
        )
        processed_languages = [
            due_date.language_code
            for due_date in existing_due_dates
            if due_date.language_code is not None
        ]

        project_languages = TranslationProject.objects.filter(
            project__code=self.project_code,
        ).values_list('language__code', flat=True)

        DueDate.objects.bulk_create(
            DueDate(
                pootle_path=re.sub(
                    r'^/projects/', '/%s/' % language, self.pootle_path,
                ),
                due_on=self.due_on,
                modified_by=self.modified_by,
                modified_on=self.modified_on,
            )
            for language in project_languages
            if language not in processed_languages
        )

    def delete(self, *args, **kwargs):
        super(DueDate, self).delete(*args, **kwargs)

        if self.language_code is not None:
            return

        DueDate.objects.for_project(self.project_code).delete()
