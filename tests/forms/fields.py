# -*- coding: utf-8 -*-
#
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import datetime

import pytest

from django.core.exceptions import ValidationError
from django.utils import dateformat, timezone

from pootle.forms.fields import UnixTimestampField


def test_unixtimestamp_clean():
    """Tests proper clean conversion when using a `UnixTimestampField`."""
    field = UnixTimestampField()
    reference_datetime = timezone.now()
    assert field.clean(reference_datetime) == reference_datetime

    timestamp = dateformat.format(reference_datetime, 'U')
    # Unix timestamps as formatted by dateformat only take seconds into account,
    # so remove potential microseconds.
    assert field.clean(timestamp) == reference_datetime.replace(microsecond=0)


@pytest.mark.parametrize('invalid_value', [
    None,
    'invalid',
    1234567890,
    datetime.date(2015, 05, 05),
])
def test_unixtimestamp_invalid(invalid_value):
    """Tests invalid values are disallowed in `UnixTimestampField`."""
    field = UnixTimestampField()
    with pytest.raises(ValidationError):
        field.clean(invalid_value)
