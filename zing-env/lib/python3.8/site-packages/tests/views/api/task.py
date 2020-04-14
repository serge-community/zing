# -*- coding: utf-8 -*-
#
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from datetime import timedelta

import pytest

from tests.factories import DueDateFactory
from tests.fixtures.models.permission_set import _require_permission_set
from tests.utils import as_dir

from pootle.core.utils.timezone import aware_datetime


@pytest.mark.django_db
def test_get_tasks_invalid_language(client, request_users, test_name, snapshot_stack):
    """Tests attempting to retrieve tasks for an invalid language."""
    url = "/xhr/tasks/invalid-language-code/"
    user = request_users["user"]

    with snapshot_stack.push([as_dir(test_name), as_dir(user.username)]):
        if not user.is_anonymous:
            client.force_login(user)
        response = client.get(url)

        with snapshot_stack.push("status_code") as snapshot:
            snapshot.assert_matches(response.status_code)

        with snapshot_stack.push("context") as snapshot:
            snapshot.assert_matches(response.json())


users_with_stats = set()


@pytest.mark.django_db
def test_get_tasks(
    client, request, request_users, test_name, snapshot_stack, patch_timezone_now
):
    """Tests pending tasks retrieval."""
    language = "language0"
    url = "/xhr/tasks/%s/" % language
    user = request_users["user"]

    # FIXME: stats refreshing boilerplate
    global users_with_stats
    if user not in users_with_stats:
        request.getfixturevalue("refresh_stats")
        users_with_stats.add(user)

    now = aware_datetime(2017, 2, 28, 9, 0)
    patch_timezone_now(now)

    DueDateFactory.create(
        pootle_path="/projects/project0/", due_on=now + timedelta(days=8),
    )
    DueDateFactory.create(
        pootle_path="/%s/project0/store0.po" % language, due_on=now + timedelta(days=2),
    )
    DueDateFactory.create(
        pootle_path="/%s/project1/store0.po" % language, due_on=now + timedelta(days=4),
    )

    with snapshot_stack.push([as_dir(test_name), as_dir(user.username)]):
        if not user.is_anonymous:
            client.force_login(user)
        response = client.get(url)

        with snapshot_stack.push("status_code") as snapshot:
            snapshot.assert_matches(response.status_code)

        with snapshot_stack.push("context") as snapshot:
            snapshot.assert_matches(response.json())


@pytest.mark.django_db
def test_get_tasks_permissions(
    client,
    test_name,
    snapshot_stack,
    refresh_stats,
    request,
    request_users,
    patch_timezone_now,
    project0,
    hide,
):
    """Tests pending tasks retrieval with restricted permissions."""
    language = "language0"
    url = "/xhr/tasks/%s/" % language
    user = request_users["user"]

    # Disallow `project0` access to `member`
    if user.username == "member":
        _require_permission_set(user, project0.directory, negative_permissions=[hide])

    # FIXME: stats refreshing boilerplate
    global users_with_stats
    if user not in users_with_stats:
        request.getfixturevalue("refresh_stats")
        users_with_stats.add(user)

    now = aware_datetime(2017, 2, 28, 9, 0)
    patch_timezone_now(now)

    DueDateFactory.create(
        pootle_path="/projects/project0/", due_on=now + timedelta(days=8),
    )
    DueDateFactory.create(
        pootle_path="/%s/project0/store0.po" % language, due_on=now + timedelta(days=2),
    )
    DueDateFactory.create(
        pootle_path="/%s/project1/store0.po" % language, due_on=now + timedelta(days=4),
    )

    with snapshot_stack.push([as_dir(test_name), as_dir(user.username)]):
        if not user.is_anonymous:
            client.force_login(user)
        response = client.get(url)

        with snapshot_stack.push("status_code") as snapshot:
            snapshot.assert_matches(response.status_code)

        with snapshot_stack.push("context") as snapshot:
            snapshot.assert_matches(response.json())
