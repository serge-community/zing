# -*- coding: utf-8 -*-
#
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import pytest

from pytest_pootle.utils import as_dir, url_name


@pytest.mark.django_db
@pytest.mark.parametrize('url', [
    '/projects/translate/',
    '/projects/project0/translate/',
    '/projects/project0/translate/store0.po',
    '/projects/project0/translate/subdir0/',
    '/projects/project0/translate/subdir0/store4.po',
    '/projects/project0/translate/empty_dir0/',
    '/projects/project0/translate/empty_dir1/store6.po',
    '/language0/translate/',
    '/language0/project0/translate/',
    '/language0/project0/translate/store0.po',
    '/language0/project0/translate/subdir0/',
    '/language0/project0/translate/subdir0/store4.po',
    '/language0/project0/translate/empty_dir0/',
    '/language0/project0/translate/empty_dir1/store6.po',
])
def test_translate(client, request_users, test_name, snapshot_stack, url):
    """Tests correctness of the translate view context."""
    user = request_users['user']

    with snapshot_stack.push([
        as_dir(test_name), as_dir(user.username), url_name(url)
    ]):
        if not user.is_anonymous():
            client.force_login(user)
        response = client.get(url)

        with snapshot_stack.push('status_code') as snapshot:
            snapshot.assert_matches(response.status_code)

        with snapshot_stack.push('context') as snapshot:
            snapshot.assert_matches(response.context)
