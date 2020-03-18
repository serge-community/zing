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
from django.utils import timezone
from django.utils.functional import cached_property

from pootle.core.url_helpers import split_pootle_path
from pootle.core.utils.list import flatten
from pootle_project.models import Project
from pootle_translationproject.models import TranslationProject

from .stats import Stats
from .task import CriticalTask, TaskResultSet, TranslationTask


def validate_pootle_path(value):
    project_code = split_pootle_path(value)[1]
    if project_code is None:
        raise ValidationError("Cannot set due date for this path.")


class DueDateQuerySet(models.QuerySet):
    def for_project_path(self, pootle_path):
        """Retrieves a queryset of due dates available for the `pootle_path`
        resource across all languages.

        :param pootle_path: internal path pointing to a project-specific
            resource.
        """
        if not pootle_path.startswith("/projects/"):
            return self.none()

        xlang_regex = r"^%s$" % re.sub(r"^/projects/", "/[^/]*/", pootle_path)
        return self.filter(pootle_path__regex=xlang_regex,).exclude(
            pootle_path__startswith="/projects/",
        )

    def for_language(self, language_code):
        """Retrieves a queryset of due dates affecting `language_code`."""
        return self.filter(pootle_path__startswith="/%s/" % language_code,)

    def accessible_by(self, user):
        """Retrieves a queryset of due dates accessible by `user`."""
        if user.is_superuser:
            return self

        project_codes = Project.objects.cached_dict(user).keys()
        project_codes_regex = "(%s)" % "|".join(project_codes)
        return self.filter(pootle_path__regex=r"^/[^/]*/%s/" % project_codes_regex,)


class FakeUser(object):
    is_superuser = True


class DueDate(models.Model):

    due_on = models.DateTimeField()
    pootle_path = models.CharField(
        max_length=255, db_index=True, unique=True, validators=[validate_pootle_path]
    )
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    modified_on = models.DateTimeField(auto_now_add=True)

    objects = DueDateQuerySet.as_manager()

    class Meta:
        indexes = (models.Index(fields=["due_on", "pootle_path", "modified_by"]),)

    @cached_property
    def stats(self):
        return Stats(self.pootle_path)

    @cached_property
    def path_parts(self):
        return split_pootle_path(self.pootle_path)

    @property
    def language_code(self):
        return self.path_parts[0]

    @property
    def project_code(self):
        return self.path_parts[1]

    @property
    def project_name(self):
        # FIXME: can we do something which doesn't require the fake user?
        try:
            return Project.objects.cached_dict(FakeUser())[self.project_code][
                "fullname"
            ]
        except KeyError:
            return self.project_code

    @classmethod
    def tasks(cls, language_code, now=None, user=None):
        """Returns a result set for top tasks which are due in `language_code`.

        :param language_code: the code of the language to retrieve tasks for.
        :param now: optionally override the value of the current datetime.
        :param user: optionally filter tasks by user's accessible projects.
        """
        due_dates = cls.objects.for_language(language_code)
        if user is not None:
            due_dates = due_dates.accessible_by(user)

        if not due_dates:
            return TaskResultSet([])

        now = now or timezone.now()
        due_tasks = list(
            flatten([due_date.get_pending_tasks(now) for due_date in due_dates])
        )

        return TaskResultSet(due_tasks).order_by_deadline()

    def __str__(self):
        return "<DueDate: %s>" % (self.due_on)

    def save(self, *args, **kwargs):
        self.full_clean()

        super().save(*args, **kwargs)

        if self.language_code is not None:
            return

        # The due date refers to a project resource: propagate changes to
        # resources at TPs
        existing_due_dates = DueDate.objects.for_project_path(self.pootle_path)
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
        ).values_list("language__code", flat=True)

        DueDate.objects.bulk_create(
            DueDate(
                pootle_path=self.get_language_path(language),
                due_on=self.due_on,
                modified_by=self.modified_by,
                modified_on=self.modified_on,
            )
            for language in project_languages
            if language not in processed_languages
        )

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

        if self.language_code is not None:
            return

        DueDate.objects.for_project_path(self.pootle_path).delete()

    def get_language_path(self, language_code):
        return re.sub(r"^/projects/", "/%s/" % language_code, self.pootle_path)

    def get_pending_tasks(self, now):
        """Gets tasks pending in the language referenced by this due date.

        :param now: `datetime` instance, point in time to determine the amount
            of time left to complete a task.
        """
        if not self.language_code:
            return []

        pending = []
        task_kwargs = {
            "due_date": self,
            "now": now,
        }

        critical_count = self.stats.critical
        if critical_count is not None and critical_count > 0:
            kwargs = dict(task_kwargs, words_left=critical_count)
            pending.append(CriticalTask(**kwargs))

        incomplete_count = self.stats.incomplete
        if incomplete_count is not None and incomplete_count > 0:
            kwargs = dict(task_kwargs, words_left=incomplete_count)
            pending.append(TranslationTask(**kwargs))

        return pending
