# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

"""Monkeypatching fixtures."""

import pytest
from _pytest.monkeypatch import MonkeyPatch


mp = MonkeyPatch()


class FakeJob(object):
    id = 'FAKE_JOB_ID'


mp.setattr('rq.get_current_job', lambda: FakeJob())


@pytest.fixture
def patch_timezone_now(monkeypatch):
    """Provides a function to monkey patch django.utils.timezone.now."""
    def _patch_fn(now_value):
        def patched_now():
            return now_value
        monkeypatch.setattr('django.utils.timezone.now', patched_now)
    return _patch_fn
