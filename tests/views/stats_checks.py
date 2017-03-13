# -*- coding: utf-8 -*-
#
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import pytest

from pytest_pootle.utils import as_dir, url_name


users_with_stats = set()


@pytest.mark.django_db
@pytest.mark.parametrize('path', [
    '/projects/',
    '/projects/project0/',
    '/projects/project0/store0.po',
    '/projects/project0/subdir0/',
    '/projects/project0/subdir0/store4.po',
    '/projects/project0/empty_dir0/',
    '/projects/project0/empty_dir1/store6.po',
    '/language0/',
    '/language0/project0/',
    '/language0/project0/store0.po',
    '/language0/project0/subdir0/',
    '/language0/project0/subdir0/store4.po',
    '/language0/project0/empty_dir0/',
    '/language0/project0/empty_dir1/store6.po',
])
def test_stats_checks(client, request_users, test_name, request,
                      snapshot_stack, path):
    """Tests the /xhr/stats/checks/ endpoint's context."""
    user = request_users['user']

    # FIXME: stats refreshing boilerplate
    global users_with_stats
    if user not in users_with_stats:
        request.getfixturevalue('refresh_stats')
        users_with_stats.add(user)

    with snapshot_stack.push([
        as_dir(test_name), as_dir(user.username), url_name(path)
    ]):
        if not user.is_anonymous:
            client.force_login(user)
        url = '/xhr/stats/checks/?path=%s' % path
        response = client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        with snapshot_stack.push('status_code') as snapshot:
            snapshot.assert_matches(response.status_code)

        with snapshot_stack.push('response_body') as snapshot:
            snapshot.assert_matches(response.json())
