# -*- coding: utf-8 -*-
#
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import pytest

from pootle.core.utils.json import remove_empty_from_dict


@pytest.mark.parametrize('input, expected_output', [
    (
        {'foo': False, 'bar': None, 'baz': 0, 'bleh': []},
        {},
    ),
    (
        {'foo': True, 'bar': 2, 'baz': 0},
        {'foo': True, 'bar': 2},
    ),
    (
        {'foo': False, 'bar': [None, 0], 'baz': 0},
        {'bar': [None, 0]},
    ),
    (
        {'foo': False, 'bar': [1, 2, 3], 'baz': 0},
        {'bar': [1, 2, 3]},
    ),
    (
        {'baz': {'foo': 0, 'bar': []}},
        {},
    ),
    (
        {'baz': {'foo': 0, 'bar': [], 'baz': [1, 2, None, False, 0]}},
        {'baz': {'baz': [1, 2, None, False, 0]}},
    ),
])
def test_remove_empty_from_dict(input, expected_output):
    """Tests in which circumstances falsy values are removed from dicts."""
    assert remove_empty_from_dict(input) == expected_output
