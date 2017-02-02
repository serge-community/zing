# -*- coding: utf-8 -*-
#
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from datetime import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from pootle.core.utils.timezone import make_aware


class UnixTimestampField(forms.Field):
    default_error_messages = {
        'invalid': _('Enter a valid time.'),
    }

    def to_python(self, value):
        if isinstance(value, datetime):
            return make_aware(value)

        if isinstance(value, int) or isinstance(value, basestring):
            try:
                value = float(value)
            except ValueError:
                pass

        if isinstance(value, float):
            try:
                return make_aware(datetime.fromtimestamp(value))
            except ValueError:
                pass

        raise ValidationError(self.error_messages['invalid'], code='invalid')
