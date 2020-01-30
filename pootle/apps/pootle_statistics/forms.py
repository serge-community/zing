# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from django import forms

from pootle.core.forms import PathForm


class StatsForm(PathForm):

    offset = forms.IntegerField(required=False)

    def clean_offset(self):
        return self.cleaned_data.get("offset", 0)
