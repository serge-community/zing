# -*- coding: utf-8 -*-
#
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from django import forms

from pootle.models import DueDate


class AddDueDateForm(forms.ModelForm):

    class Meta:
        model = DueDate
        fields = ('due_on', 'pootle_path', 'modified_by', )

    def clean_due_on(self):
        data = self.cleaned_data['due_on']
        # Always set to `09:00:00` in the server's timezone
        data = data.replace(hour=9, minute=0, second=0, microsecond=0)
        return data


class EditDueDateForm(AddDueDateForm):

    class Meta:
        model = DueDate
        fields = ('due_on', )
