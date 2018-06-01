# -*- coding: utf-8 -*-
#
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import pytest

from tests.utils import as_dir, url_name

from pootle.models import Stats


@pytest.mark.django_db
def test_stats_retrieval(test_name, snapshot_stack, refresh_stats):
    """Tests stats values are retrieved properly."""
    path = '/language0/project0/'
    with snapshot_stack.push([as_dir(test_name), url_name(path)]) as snapshot:
        stats = Stats(path)
        stats_data = {
            'total': stats.total,
            'translated': stats.translated,
            'fuzzy': stats.fuzzy,
            'incomplete': stats.incomplete,
            'critical': stats.critical,
            'suggestions': stats.suggestions,
            'last_action': stats.last_action,
            'last_updated': stats.last_updated,
        }
        snapshot.assert_matches(stats_data)


@pytest.mark.django_db
def test_stats_retrieval_dummy(test_name, snapshot_stack, refresh_stats):
    """Tests no stats are provided for dummy paths."""
    path = '/non/existing/'
    with snapshot_stack.push([as_dir(test_name), url_name(path)]) as snapshot:
        stats = Stats(path)
        stats_data = {
            'total': stats.total,
            'translated': stats.translated,
            'fuzzy': stats.fuzzy,
            'incomplete': stats.incomplete,
            'critical': stats.critical,
            'suggestions': stats.suggestions,
            'last_action': stats.last_action,
            'last_updated': stats.last_updated,
        }
        snapshot.assert_matches(stats_data)


@pytest.mark.django_db
def test_stats_retrieval_no_stats(test_name, snapshot_stack, flush_stats):
    """Tests no stats are provided when these haven't been calculated."""
    path = '/language0/project0/'
    with snapshot_stack.push([as_dir(test_name), url_name(path)]) as snapshot:
        stats = Stats(path)
        stats_data = {
            'total': stats.total,
            'translated': stats.translated,
            'fuzzy': stats.fuzzy,
            'incomplete': stats.incomplete,
            'critical': stats.critical,
            'suggestions': stats.suggestions,
            'last_action': stats.last_action,
            'last_updated': stats.last_updated,
        }
        snapshot.assert_matches(stats_data)
