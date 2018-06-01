# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import functools
import urllib
from collections import OrderedDict

import pytest

from django.urls import reverse

from tests.utils import get_test_uids


BAD_VIEW_TESTS = OrderedDict((
    ('/foo/bar', dict(code=301, location='/foo/bar/')),
    ('/foo/bar/', {}),
    ('/projects', dict(code=301, location='/projects/')),
    ('/projects/project0',
     dict(code=301, location='/projects/project0/')),
    ('/projects/project0/foo.po', {}),
    ('/projects/projectfoo',
     dict(code=301, location='/projects/projectfoo/')),
    ('/projects/projectfoo/', {}),
    ('/language0/projectfoo',
     dict(code=301, location='/language0/projectfoo/')),
    ('/language0/projectfoo/', {}),
    ('/language0/project0',
     dict(code=301, location='/language0/project0/')),
    ('/projects/project0/subdir0/foo.po', {}),
    # these may not be correct - but are current behaviour
    ('/language0/project0/foo/',
     dict(code=302, location='/language0/project0/')),
    ('/language0/project0/foo',
     dict(code=302, location='/language0/project0/')),
    ('/language0/project0/subdir0',
     dict(code=302, location='/language0/project0/')),

    ('/projects/PROJECT0/', {}),
    ('/language0/PROJECT0/', {}),
    ('/language0/PROJECT0/subdir0/', {}),
    ('/language0/PROJECT0/store0.po', {}),

    ('/LANGUAGE0/',
     dict(code=301, location='/language0/')),
    ('/LANGUAGE0/foo/',
     dict(code=301, location='/language0/foo/')),
    ('/LANGUAGE0/project0/',
     dict(code=301, location='/language0/project0/')),
    ('/LANGUAGE0/project0/subdir0/',
     dict(code=301, location='/language0/project0/subdir0/')),
    ('/LANGUAGE0/project0/store0.po',
     dict(code=301, location='/language0/project0/store0.po')),

    ('/xhr/units/1/edit/', dict(code=400)),

    ('/xhr/uids/?path=/%s' % ('BAD' * 800),
     dict(ajax=True, code=400)),
    ('/xhr/uids/?filter=translated&path=/',
     dict(ajax=True)),

    ('/xhr/units/?uids=BOBO',
     dict(ajax=True, code=400)),
))

GET_UNITS_TESTS = OrderedDict(
    (("default_path", {}),
     ("root_path", dict(path="/")),
     ("projects_path", dict(path="/projects/")),
     ("project_path", dict(path="/projects/project0/")),
     ("bad_project_path", dict(path="/projects/FOO/")),
     ("state_translated",
      {"filter": "translated"}),
     ("state_translated_continued",
      {"filter": "translated",
       "uids": functools.partial(get_test_uids, count=9),
       "offset": 10}),
     ("state_untranslated",
      {"filter": "untranslated"}),
     ("state_untranslated",
      {"filter": "untranslated",
       "offset": 100000}),
     ("state_incomplete",
      {"filter": "incomplete"}),
     ("state_fuzzy",
      {"filter": "fuzzy"}),
     ("sort_units_oldest",
      {"sort_by_param": "oldest"}),
     ("filter_from_uid",
      {"path": "/language0/project0/store0.po",
       "uids": functools.partial(get_test_uids,
                                 pootle_path="/language0/project0/store0.po"),
       "filter": "all"}),
     ("translated_by_member",
      {"filter": "translated",
       "user": "member"}),
     ("translated_by_member_FOO",
      {"filter": "translated",
       "user": "member_FOO"}),
     ("filter_suggestions",
      {"filter": "suggestions"}),
     ("filter_user_suggestions",
      {"filter": "user-suggestions"}),
     ("filter_user_suggestions_accepted",
      {"filter": "user-suggestions-accepted"}),
     ("filter_user_suggestions_rejected",
      {"filter": "user-suggestions-rejected"}),
     ("filter_user_submissions",
      {"filter": "user-submissions"}),
     ("filter_user_submissions_overwritten",
      {"filter": "user-submissions-overwritten"}),
     ("filter_search_empty",
      {"search": "SEARCH_NOT_EXIST",
       "sfields": "source"}),
     ("filter_search_untranslated",
      {"search": "untranslated",
       "sfields": "source"}),
     ("filter_search_sfields_multi",
      {"search": "SEARCH_NOT_EXIST",
       "sfields": "source,target"}),
     ("sort_user_suggestion_newest",
      {"sort": "newest",
       "filter": "user-suggestions"}),
     ("sort_user_suggestion_oldest",
      {"sort": "oldest",
       "filter": "user-suggestions"}),
     ("checks_foo",
      {"filter": "checks",
       "checks": "foo"}),
     ("checks_endpunc",
      {"filter": "checks",
       "checks": ["endpunc"]}),
     ("checks_category_critical",
      {"filter": "checks",
       "category": "critical"})))

DISABLED_PROJECT_URL_PARAMS = OrderedDict(
    (("project", {
        "view_name": "pootle-project",
        "project_code": "disabled_project0",
        "dir_path": "",
        "filename": ""}),
     ("tp", {
         "view_name": "pootle-tp",
         "project_code": "disabled_project0",
         "language_code": "language0",
         "dir_path": ""}),
     ("tp_subdir", {
         "view_name": "pootle-tp",
         "project_code": "disabled_project0",
         "language_code": "language0",
         "dir_path": "subdir0/"}),
     ("tp_store", {
         "view_name": "pootle-tp-store",
         "project_code": "disabled_project0",
         "language_code": "language0",
         "dir_path": "",
         "filename": "store0.po"}),
     ("tp_subdir_store", {
         "view_name": "pootle-tp-store",
         "project_code": "disabled_project0",
         "language_code": "language0",
         "dir_path": "subdir0/",
         "filename": "store1.po"})))


@pytest.fixture(params=GET_UNITS_TESTS.keys())
def get_units_views(request, client, request_users):
    params = GET_UNITS_TESTS[request.param].copy()
    params["path"] = params.get("path", "/language0/")

    user = request_users["user"]
    if user.username != "nobody":
        client.force_login(user)

    url_params = urllib.urlencode(params, True)
    response = client.get(
        "%s?%s"
        % (reverse("pootle-xhr-uids"),
           url_params),
        HTTP_X_REQUESTED_WITH='XMLHttpRequest')

    params["pootle_path"] = params["path"]
    return user, params, url_params, response


@pytest.fixture(params=BAD_VIEW_TESTS.keys())
def bad_views(request, client):
    url = request.param
    test = dict(code=404)
    test.update(BAD_VIEW_TESTS[url])
    if test.get("ajax"):
        response = client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    else:
        response = client.get(url)
    return (url, response, test)


@pytest.fixture(params=("browse", "translate", "export"))
def view_types(request):
    """List of possible view types."""
    return request.param


@pytest.fixture(params=DISABLED_PROJECT_URL_PARAMS.keys())
def dp_view_urls(request, view_types):
    """List of url params required for disabled project tests."""
    kwargs = DISABLED_PROJECT_URL_PARAMS[request.param].copy()
    view_name = kwargs.pop("view_name")
    view_name = "%s-%s" % (view_name, view_types)

    return reverse(view_name, kwargs=kwargs)
