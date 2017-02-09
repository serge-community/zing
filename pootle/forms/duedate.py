# -*- coding: utf-8 -*-
#
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from django import forms

from pootle.models import DueDate


# Set all due on times to this specific time of the day (in server's TZ)
DUE_ON_HOUR = 9
DUE_ON_MINUTE = 0


class AddDueDateForm(forms.ModelForm):

    class Meta:
        model = DueDate
        fields = ('due_on', 'pootle_path', 'modified_by', )

    def clean_due_on(self):
        data = self.cleaned_data['due_on']
        data = data.replace(
            hour=DUE_ON_HOUR, minute=DUE_ON_MINUTE, second=0, microsecond=0,
        )
        return data


class EditDueDateForm(AddDueDateForm):

    class Meta:
        model = DueDate
        fields = ('due_on', )
