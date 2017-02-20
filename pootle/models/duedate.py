# -*- coding: utf-8 -*-
#
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

INVALID_POOTLE_PATHS = ['/', '/projects/']


def validate_pootle_path(value):
    if value in INVALID_POOTLE_PATHS:
        raise ValidationError('Cannot set due date for this path.')


class DueDate(models.Model):

    due_on = models.DateTimeField()
    pootle_path = models.CharField(max_length=255, db_index=True, unique=True,
                                   validators=[validate_pootle_path])
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    modified_on = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'<DueDate: %s>' % (self.due_on)

    def save(self, *args, **kwargs):
        self.full_clean()

        super(DueDate, self).save(*args, **kwargs)
