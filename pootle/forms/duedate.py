# -*- coding: utf-8 -*-
#
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from django import forms

from pootle.forms.fields import UnixTimestampField
from pootle.models import DueDate


class AddDueDateForm(forms.ModelForm):

    due_on = UnixTimestampField()

    class Meta:
        model = DueDate
        fields = ('due_on', 'pootle_path', 'modified_by', )


class EditDueDateForm(AddDueDateForm):

    class Meta:
        model = DueDate
        fields = ('due_on', )
