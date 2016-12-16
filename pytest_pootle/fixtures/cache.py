# -*- coding: utf-8 -*-
#
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import pytest

from django_redis import get_redis_connection


@pytest.fixture
def flush_redis():
    """Clears Redis persistent store."""
    get_redis_connection('redis').flushdb()


@pytest.fixture
def flush_stats():
    """Flushes stats cache."""
    get_redis_connection('stats').flushdb()


@pytest.fixture
def refresh_stats(flush_stats):
    """Ensures stats are calculated."""
    from pootle_store.models import Store
    for store in Store.objects.live().iterator():
        store.update_all_cache()
