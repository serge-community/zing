# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import json
from urlparse import parse_qs

import pytest

from pytest_pootle.search import calculate_search_results

from pootle_app.models import Directory
from pootle_app.models.permissions import check_user_permission
from pootle_project.models import Project


@pytest.mark.django_db
@pytest.mark.xfail(reason='this test needs to be replaced with snapshot-based one')
def test_get_units(get_units_views):
    (user, search_params, url_params, response) = get_units_views
    result = json.loads(response.content)

    path = parse_qs(url_params)["path"][0]

    permission_context = None
    if path.strip("/") in ["", "projects"]:
        permission_context = Directory.objects.get(pootle_path="/projects/")
    elif path.startswith("/projects/"):
        try:
            permission_context = Project.objects.get(
                code=path[10:].split("/")[0]).directory
        except Project.DoesNotExist:
            assert response.status_code == 404
            assert "unitGroups" not in result
            return

    user_cannot_view = (
        permission_context
        and not check_user_permission(
            user, "administrate", permission_context))
    if user_cannot_view:
        assert response.status_code == 404
        assert "unitGroups" not in result
        return

    assert "unitGroups" in result
    assert isinstance(result["unitGroups"], list)

    for k in "start", "end", "total":
        assert k in result
        assert isinstance(result[k], int)

    if result["unitGroups"]:
        total, start, end, expected_units = calculate_search_results(
            search_params, user)

        assert result["total"] == total
        assert result["start"] == start
        assert result["end"] == end

        for i, group in enumerate(expected_units):
            result_group = result["unitGroups"][i]
            for store, data in group.items():
                result_data = result_group[store]
                assert (
                    [u["id"] for u in result_data["units"]]
                    == [u["id"] for u in data["units"]])
