# -*- coding: utf-8 -*-
#
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from datetime import datetime

import pytest
import pytz

from django.utils import timezone

from pootle_misc.util import get_max_month_datetime


@pytest.fixture(params=[
    'UTC',
    'America/Los_Angeles',
    'Europe/Helsinki',
])
def tz_name(request):
    return request.param


@pytest.mark.parametrize('input, expected', [
    (
        datetime(2017, 3, 1, 23, 55, 0),
        datetime(2017, 3, 31, 23, 59, 59, 999999),
    ),
    (
        datetime(2017, 4, 1, 23, 55, 0),
        datetime(2017, 4, 30, 23, 59, 59, 999999),
    ),
    (
        datetime(2017, 10, 1, 0, 0, 0),
        datetime(2017, 10, 31, 23, 59, 59, 999999),
    ),
    (
        datetime(2017, 11, 1, 0, 0, 0),
        datetime(2017, 11, 30, 23, 59, 59, 999999),
    ),
    (
        datetime(2017, 12, 1, 0, 0, 0),
        datetime(2017, 12, 31, 23, 59, 59, 999999),
    ),
])
def test_get_max_month_datetime(input, expected, settings, tz_name):
    settings.TIME_ZONE = tz_name
    input_dt = timezone.make_aware(input, timezone=pytz.timezone(tz_name))
    expected_dt = timezone.make_aware(expected, timezone=pytz.timezone(tz_name))

    assert get_max_month_datetime(input_dt) == expected_dt
