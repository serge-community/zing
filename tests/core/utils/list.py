# -*- coding: utf-8 -*-
#
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import pytest

from pootle.core.utils.list import flatten


@pytest.mark.parametrize('input, expected', [
    ([], []),
    ([1, 2, 3], [1, 2, 3]),
    ([1, [2], 3], [1, 2, 3]),
    ([1, [2, 3]], [1, 2, 3]),
    ([[1], [2, 3], 'foo'], [1, 2, 3, 'foo']),
    ([[1], [2, [3]], 'foo'], [1, 2, 3, 'foo']),
    ([[1], [2, [3]], ['foo', 'bar']], [1, 2, 3, 'foo', 'bar']),
])
def test_flatten(input, expected):
    """Tests list flattening."""
    assert list(flatten(input)) == expected
