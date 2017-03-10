# -*- coding: utf-8 -*-
#
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from django import forms

from pootle_language.models import Language


MIN_PENDING_TASKS = 3
PENDING_TASKS_LIMIT = 5


class GetTaskForm(forms.Form):

    language = forms.ModelChoiceField(
        queryset=Language.live.all(),
        to_field_name='code',
    )
    offset = forms.IntegerField(required=False)
    limit = forms.IntegerField(required=False)

    def clean_offset(self):
        return self.cleaned_data.get('offset') or 0

    def clean_limit(self):
        limit = self.cleaned_data.get('limit') or PENDING_TASKS_LIMIT
        # Allow at max 2 times the limit of tasks. This can be useful
        # when the tasks list is expanded to more than `PENDING_TASKS_LIMIT`
        # items and we want to refresh the existing items right away.
        return max(MIN_PENDING_TASKS, min(limit, 2 * PENDING_TASKS_LIMIT))
