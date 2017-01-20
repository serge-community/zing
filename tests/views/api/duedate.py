# -*- coding: utf-8 -*-
#
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from datetime import datetime

import pytest

from django.utils import dateformat

from pytest_pootle.factories import DueDateFactory
from pytest_pootle.utils import as_dir, url_name

from pootle.core.utils.json import jsonify
from pootle.core.utils.timezone import aware_datetime


@pytest.mark.django_db
@pytest.mark.parametrize('path', [
    '/projects/',
    '/projects/project0/',
    '/projects/project0/store0.po',
    '/projects/project0/subdir0/',
    '/projects/project0/subdir0/store4.po',
    '/language0/',
    '/language0/project0/',
    '/language0/project0/store0.po',
    '/language0/project0/subdir0/',
    '/language0/project0/subdir0/store4.po',
])
def test_duedate_post(client, request_users, test_name, snapshot_stack, path):
    """Tests creating new due dates."""
    url = '/xhr/duedates/'
    user = request_users['user']
    post_data = {
        'due_on': dateformat.format(datetime(2017, 01, 26, 01, 02, 03), 'U'),
        'modified_by': user.id,
        'pootle_path': path,
    }

    with snapshot_stack.push([
        as_dir(test_name), as_dir(user.username), url_name(path)
    ]):
        if not user.is_anonymous():
            client.force_login(user)
        response = client.post(url, jsonify(post_data),
                               content_type='application/json')

        with snapshot_stack.push('status_code') as snapshot:
            snapshot.assert_matches(response.status_code)

        with snapshot_stack.push('context') as snapshot:
            snapshot.assert_matches(response.json())


@pytest.mark.django_db
@pytest.mark.parametrize('path', [
    '/projects/project0/',
    '/projects/project0/store0.po',
    '/projects/project0/subdir0/',
    '/projects/project0/subdir0/store4.po',
    '/language0/',
    '/language0/project0/',
    '/language0/project0/store0.po',
    '/language0/project0/subdir0/',
    '/language0/project0/subdir0/store4.po',
])
def test_duedate_update(client, request_users, test_name, snapshot_stack, path):
    """Tests updating existing due dates."""
    user = request_users['user']

    initial_due_on = aware_datetime(2017, 01, 26, 01, 02, 03)
    data = {
        'due_on': initial_due_on,
        'modified_by': user,
        'pootle_path': path,
    }
    due_date = DueDateFactory.create(**data)
    assert due_date.id is not None

    url = '/xhr/duedates/%s/' % due_date.id
    put_data = {
        'due_on': dateformat.format(aware_datetime(2017, 01, 27, 01, 02, 03), 'U'),
        'modified_by': user.id,
        'pootle_path': path,
    }

    with snapshot_stack.push([
        as_dir(test_name), as_dir(user.username), url_name(path)
    ]):
        if not user.is_anonymous():
            client.force_login(user)
        response = client.put(url, jsonify(put_data),
                              content_type='application/json')

        if response.status_code == 200:
            due_date.refresh_from_db()
            assert due_date.due_on != initial_due_on

        with snapshot_stack.push('status_code') as snapshot:
            snapshot.assert_matches(response.status_code)

        with snapshot_stack.push('context') as snapshot:
            snapshot.assert_matches(response.json())


@pytest.mark.django_db
@pytest.mark.parametrize('path', [
    '/projects/project0/',
    '/projects/project0/store0.po',
    '/projects/project0/subdir0/',
    '/projects/project0/subdir0/store4.po',
    '/language0/',
    '/language0/project0/',
    '/language0/project0/store0.po',
    '/language0/project0/subdir0/',
    '/language0/project0/subdir0/store4.po',
])
def test_duedate_delete(client, request_users, test_name, snapshot_stack, path):
    """Tests removing existing due dates."""
    user = request_users['user']

    data = {
        'due_on': datetime.now(),
        'modified_by': user,
        'pootle_path': path,
    }
    due_date = DueDateFactory.create(**data)
    assert due_date.id is not None

    url = '/xhr/duedates/%s/' % due_date.id

    with snapshot_stack.push([
        as_dir(test_name), as_dir(user.username), url_name(path)
    ]):
        if not user.is_anonymous():
            client.force_login(user)
        response = client.delete(url, content_type='application/json')

        with snapshot_stack.push('status_code') as snapshot:
            snapshot.assert_matches(response.status_code)

        with snapshot_stack.push('context') as snapshot:
            snapshot.assert_matches(response.json())


@pytest.mark.django_db
@pytest.mark.parametrize('path', [
    '/projects/fake-project/',
    '/projects/fake-project/store0.po',
    '/fake-language/',
    '/fake-language/fake-project/',
    '/fake-language/fake-project/fake-store.po',
])
def test_duedate_post_fake_paths(client, admin, path):
    """Tests posting with fake/invalid paths.

    This basically checks the logic behind `CanAdminPath`, but could probably
    belong somewhere else too.
    """
    url = '/xhr/duedates/'
    post_data = {
        'due_on': dateformat.format(datetime(2017, 01, 26, 01, 02, 03), 'U'),
        'modified_by': admin.id,
        'pootle_path': path,
    }

    client.force_login(admin)
    response = client.post(url, jsonify(post_data),
                           content_type='application/json')

    assert response.status_code == 404
    assert response.json() == {'msg': 'Not found'}
