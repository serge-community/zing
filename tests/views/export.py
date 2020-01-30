# -*- coding: utf-8 -*-
#
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import pytest

from tests.utils import as_dir, url_name


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url",
    [
        "/projects/export-view/",
        "/projects/project0/export-view/",
        "/projects/project0/export-view/store0.po",
        "/projects/project0/export-view/subdir0/",
        "/projects/project0/export-view/subdir0/store4.po",
        "/projects/project0/export-view/empty_dir0/",
        "/projects/project0/export-view/empty_dir1/store6.po",
        "/language0/export-view/",
        "/language0/project0/export-view/",
        "/language0/project0/export-view/store0.po",
        "/language0/project0/export-view/subdir0/",
        "/language0/project0/export-view/subdir0/store4.po",
        "/language0/project0/export-view/empty_dir0/",
        "/language0/project0/export-view/empty_dir1/store6.po",
    ],
)
@pytest.mark.parametrize("limit", [None, 1])
def test_export(
    client, request_users, test_name, monkeypatch, snapshot_stack, url, limit
):
    """Tests correctness of the export view context."""
    user = request_users["user"]

    stack = [as_dir(test_name), as_dir(user.username), url_name(url)]
    if limit is not None:
        stack.append("limit=%s" % limit)
        monkeypatch.setattr("pootle.core.views.export.UNITS_LIMIT", limit)

    with snapshot_stack.push(stack):
        if not user.is_anonymous:
            client.force_login(user)
        response = client.get(url)

        with snapshot_stack.push("status_code") as snapshot:
            snapshot.assert_matches(response.status_code)

        with snapshot_stack.push("context") as snapshot:
            snapshot.assert_matches(response.context)
