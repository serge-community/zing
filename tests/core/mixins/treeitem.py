# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import pytest

from pootle.core.mixins.treeitem import CachedMethods, CachedTreeItem
from pootle_app.models import Directory
from pootle_project.models import Project
from pootle_store.models import Store
from pootle_translationproject.models import TranslationProject


def test_cachedmethods_get_all():
    """Retrieval of all cached methods as a list."""
    ALL_CACHED_METHODS = [
        "get_checks",
        "get_last_action",
        "get_last_updated",
        "get_mtime",
        "get_suggestion_count",
        "get_wordcount_stats",
    ]
    assert CachedMethods.get_all() == ALL_CACHED_METHODS


def test_cachedmethods_str():
    """Make sure coercion to str() prints enum's value."""
    assert str(CachedMethods.WORDCOUNT_STATS) == "get_wordcount_stats"


def test_cachedtreeitem_get_set_cached_value():
    """Setting/getting cached values via method names."""
    cti = CachedTreeItem()
    cti.pootle_path = "/test/path/"  # dummy value required for `cache_key`

    method = CachedMethods.WORDCOUNT_STATS
    expected_value = "test_value"

    cti.set_cached_value(method, expected_value)
    assert cti.get_cached_value(method) == expected_value


@pytest.mark.django_db
def test_get_children(project0, language0):
    """Ensure that retrieved child objects have a correct type."""

    def _all_children_are_directories_or_stores(item):
        for child in item.children:
            if isinstance(child, Directory):
                _all_children_are_directories_or_stores(child)
            else:
                assert isinstance(child, Store)

    for tp in project0.children:
        assert isinstance(tp, TranslationProject)
        _all_children_are_directories_or_stores(tp)

    for tp in language0.children:
        assert isinstance(tp, TranslationProject)
        _all_children_are_directories_or_stores(tp)


@pytest.mark.django_db
def test_get_parent(po_directory, project0, language0, tp0, store0, subdir0):
    """Ensure that retrieved parent objects have a correct type."""

    subdir_store = subdir0.child_stores.first()
    parent = subdir_store.get_parent()
    assert isinstance(parent, Directory)

    parent = store0.get_parent()
    assert isinstance(parent, TranslationProject)

    parent = tp0.get_parent()
    assert isinstance(parent, Project)

    parent = tp0.directory.get_parent()
    assert isinstance(parent, Project)

    parent = project0.directory.get_parent()
    assert parent is None

    parent = language0.directory.get_parent()
    assert parent is None
