# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import pytest


@pytest.mark.django_db
def test_views_disabled_project(client, dp_view_urls, request_users):
    url = dp_view_urls
    user = request_users["user"]
    if user.username != "nobody":
        client.force_login(user)

    response = client.get(url)

    if user.is_superuser:
        assert response.status_code == 200
    else:
        assert response.status_code == 404
