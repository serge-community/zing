# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from itertools import groupby

import pytest

from pytest_pootle.suite import view_context_test

from pootle_app.models.permissions import check_permission
from pootle.core.delegate import search_backend
from pootle.core.helpers import get_filter_name
from pootle.core.url_helpers import get_previous_url, get_path_parts
from pootle_misc.checks import get_qualitycheck_schema
from pootle_misc.forms import make_search_form
from pootle_store.forms import UnitExportForm
from pootle_store.models import Unit


def _test_translate_view(tp, request, response, kwargs, settings):
    ctx = response.context
    kwargs["project_code"] = tp.project.code
    kwargs["language_code"] = tp.language.code
    resource_path = "%(dir_path)s%(filename)s" % kwargs
    request_path = "%s%s" % (tp.pootle_path, resource_path)
    assertions = dict(
        page="translate",
        translation_project=tp,
        language=tp.language,
        project=tp.project,
        has_admin_access=check_permission('administrate', request),
        ctx_path=tp.pootle_path,
        pootle_path=request_path,
        resource_path=resource_path,
        resource_path_parts=get_path_parts(resource_path),
        editor_extends="translation_projects/base.html",
        check_categories=get_qualitycheck_schema(),
        previous_url=get_previous_url(request),
        cantranslate=check_permission("translate", request),
        cansuggest=check_permission("suggest", request),
        canreview=check_permission("review", request),
        search_form=make_search_form(request=request),
        POOTLE_MT_BACKENDS=settings.POOTLE_MT_BACKENDS,
    )
    view_context_test(ctx, **assertions)


def _test_export_view(tp, request, response, kwargs, settings):
    ctx = response.context
    filter_name, filter_extra = get_filter_name(request.GET)
    form_data = request.GET.copy()
    form_data["path"] = request.path.replace("export-view/", "")
    search_form = UnitExportForm(
        form_data, user=request.user)
    assert search_form.is_valid()
    total, start_, end_, units_qs = search_backend.get(Unit)(
        request.user, **search_form.cleaned_data).search()
    units_qs = units_qs.select_related('store')
    assertions = {}
    if total > settings.POOTLE_EXPORT_VIEW_LIMIT:
        units_qs = units_qs[:settings.POOTLE_EXPORT_VIEW_LIMIT]
        assertions.update(
            {'unit_total_count': total,
             'displayed_unit_count': settings.POOTLE_EXPORT_VIEW_LIMIT})
    unit_groups = [
        (path, list(units))
        for path, units
        in groupby(
            units_qs,
            lambda x: x.store.pootle_path)]
    assertions.update(
        dict(project=tp.project,
             language=tp.language,
             source_language=tp.project.source_language,
             filter_name=filter_name,
             filter_extra=filter_extra,
             unit_groups=unit_groups))
    view_context_test(ctx, **assertions)


@pytest.mark.django_db
def test_views_tp(tp_views, settings):
    test_type, tp, request, response, kwargs = tp_views
    if test_type == "translate":
        _test_translate_view(tp, request, response, kwargs, settings)
    else:
        _test_export_view(tp, request, response, kwargs, settings)


@pytest.mark.django_db
def test_view_user_choice(client):

    client.cookies["user-choice"] = "language"
    response = client.get("/foo/bar/baz")
    assert response.status_code == 302
    assert response.get("location") == "/foo/"
    assert "user-choice" not in response

    client.cookies["user-choice"] = "project"
    response = client.get("/foo/bar/baz")
    assert response.status_code == 302
    assert response.get("location") == "/projects/bar/"
    assert "user-choice" not in response

    client.cookies["user-choice"] = "foo"
    response = client.get("/foo/bar/baz")
    assert response.status_code == 404
    assert "user-choice" not in response
