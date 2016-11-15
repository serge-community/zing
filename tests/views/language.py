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
from pootle.core.url_helpers import get_previous_url
from pootle_misc.checks import get_qualitycheck_schema
from pootle_misc.forms import make_search_form
from pootle_store.forms import UnitExportForm
from pootle_store.models import Unit


def _test_translate_view(language, request, response, kwargs, settings):
    ctx = response.context
    view_context_test(
        ctx,
        **dict(
            project=None,
            language=language,
            page="translate",
            ctx_path=language.directory.pootle_path,
            pootle_path=language.directory.pootle_path,
            resource_path="",
            resource_path_parts=[],
            editor_extends="languages/base.html",
            check_categories=get_qualitycheck_schema(),
            previous_url=get_previous_url(request),
            has_admin_access=check_permission('administrate', request),
            cantranslate=check_permission("translate", request),
            cansuggest=check_permission("suggest", request),
            canreview=check_permission("review", request),
            search_form=make_search_form(request=request),
            POOTLE_MT_BACKENDS=settings.POOTLE_MT_BACKENDS,
        )
    )


def _test_export_view(language, request, response, kwargs):
    # TODO: export views should be parsed in a form
    ctx = response.context
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
    view_context_test(
        ctx,
        **dict(
            project=None,
            language=language,
            source_language="en",
            filter_name=filter_name,
            filter_extra=filter_extra,
            unit_groups=unit_groups))


@pytest.mark.django_db
def test_views_language(language_views, settings):
    test_type, language, request, response, kwargs = language_views
    if test_type == "browse":
        pytest.xfail(
            reason='this test needs to be replaced with snapshot-based one'
        )
    if test_type == "translate":
        _test_translate_view(language, request, response, kwargs, settings)
    elif test_type == "export":
        _test_export_view(language, request, response, kwargs)
