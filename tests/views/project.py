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

from django.core.urlresolvers import reverse

from pytest_pootle.suite import view_context_test

from pootle_app.models.permissions import check_permission
from pootle.core.delegate import search_backend
from pootle.core.helpers import get_filter_name
from pootle.core.url_helpers import get_previous_url
from pootle.core.views.export import UNITS_LIMIT
from pootle_misc.checks import get_qualitycheck_schema
from pootle_misc.forms import make_search_form
from pootle_store.forms import UnitExportForm
from pootle_store.models import Unit


def _test_export_view(project, request, response, kwargs, settings):
    if not request.user.is_superuser:
        assert response.status_code == 403
        return

    ctx = response.context
    kwargs["project_code"] = project.code
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
    if total > UNITS_LIMIT:
        units_qs = units_qs[:UNITS_LIMIT]
        assertions.update(
            {'unit_total_count': total,
             'displayed_unit_count': UNITS_LIMIT})
    unit_groups = [
        (path, list(units))
        for path, units
        in groupby(
            units_qs,
            lambda x: x.store.pootle_path)]
    assertions.update(
        dict(project=project,
             language=None,
             source_language="en",
             filter_name=filter_name,
             filter_extra=filter_extra,
             unit_groups=unit_groups))
    view_context_test(ctx, **assertions)


@pytest.mark.django_db
def test_views_project(project_views, settings):
    test_type, project, request, response, kwargs = project_views
    if test_type == "export":
        _test_export_view(project, request, response, kwargs, settings)


@pytest.mark.django_db
def test_view_projects_translate(client, settings, request_users):
    user = request_users["user"]
    client.force_login(user)
    response = client.get(reverse("pootle-projects-translate"))

    if not user.is_superuser:
        assert response.status_code == 403
        return

    ctx = response.context
    request = response.wsgi_request
    assertions = dict(
        page="translate",
        has_admin_access=user.is_superuser,
        language=None,
        project=None,
        pootle_path="/projects/",
        ctx_path="/projects/",
        resource_path="",
        resource_path_parts=[],
        editor_extends="projects/all/base.html",
        check_categories=get_qualitycheck_schema(),
        previous_url=get_previous_url(request),
        cantranslate=check_permission("translate", request),
        cansuggest=check_permission("suggest", request),
        canreview=check_permission("review", request),
        search_form=make_search_form(request=request),
        POOTLE_MT_BACKENDS=settings.POOTLE_MT_BACKENDS,
    )
    view_context_test(ctx, **assertions)


@pytest.mark.django_db
def test_view_projects_export(client):
    response = client.get(reverse("pootle-projects-export"))
    ctx = response.context
    request = response.wsgi_request

    if not request.user.is_superuser:
        assert response.status_code == 403
        return

    filter_name, filter_extra = get_filter_name(request.GET)
    form_data = request.GET.copy()
    form_data["path"] = request.path.replace("export-view/", "")
    search_form = UnitExportForm(
        form_data, user=request.user)
    assert search_form.is_valid()
    total_, start_, end_, units_qs = search_backend.get(Unit)(
        request.user, **search_form.cleaned_data).search()
    units_qs = units_qs.select_related('store')
    unit_groups = [
        (path, list(units))
        for path, units
        in groupby(
            units_qs,
            lambda x: x.store.pootle_path)]
    assertions = dict(
        project=None,
        language=None,
        source_language="en",
        filter_name=filter_name,
        filter_extra=filter_extra,
        unit_groups=unit_groups)
    view_context_test(ctx, **assertions)
