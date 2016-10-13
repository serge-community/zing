# -*- coding: utf-8 -*-
#
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import fakeredis
import pytest


@pytest.fixture
def flush_redis():
    """Flushes fakeredis' module-level state."""
    redis_conn = fakeredis.FakeStrictRedis()
    redis_conn.flushall()
