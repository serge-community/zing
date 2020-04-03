# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import urllib.parse

import pytest

from tests.utils import as_dir, url_name

users_with_stats = set()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "params",
    [
        {"path": "/projects/"},
        {"path": "/projects/", "all": ""},
        {"path": "/projects/project0/"},
        {"path": "/projects/project0/", "all": ""},
        {"path": "/language0/"},
        {"path": "/language0/", "all": ""},
        {"path": "/language0/project0/"},
        {"path": "/language0/project0/", "all": ""},
    ],
)
def test_get_stats(client, request_users, test_name, request, snapshot_stack, params):
    """Tests the /xhr/stats/ view."""
    url = "/xhr/stats/"
    user = request_users["user"]

    # stats refreshing boilerplate
    global users_with_stats
    if user not in users_with_stats:
        request.getfixturevalue("refresh_stats")
        users_with_stats.add(user)

    qs = urllib.parse.urlencode(params, True)
    with snapshot_stack.push(
        [as_dir(test_name), as_dir(user.username), url_name(url + qs)]
    ):
        if not user.is_anonymous:
            client.force_login(user)
        response = client.get(url, params, HTTP_X_REQUESTED_WITH="XMLHttpRequest")

        with snapshot_stack.push("status_code") as snapshot:
            snapshot.assert_matches(response.status_code)

        with snapshot_stack.push("response") as snapshot:
            snapshot.assert_matches(response.json())
