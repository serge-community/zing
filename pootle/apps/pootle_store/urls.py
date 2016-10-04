# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from django.conf.urls import url

from . import views


urlpatterns = [
    # permalinks
    url(r'^unit/(?P<uid>[0-9]+)/?$',
        views.permalink_redirect,
        name='pootle-unit-permalink'),

    # XHR
    url(r'^xhr/stats/checks/?$',
        views.get_qualitycheck_stats,
        name='pootle-xhr-stats-checks'),
    # FIXME: even if the semantics changed, keeping the URL as-is for now for
    # pure convenience: stats.js requires further changes which might end up
    # being not be necessary in the near future.
    url(r'^xhr/stats/?$',
        views.BrowseDataDispatcherView.as_view(),
        name='pootle-xhr-stats'),

    url(r'^xhr/uids/?$',
        views.get_uids,
        name='pootle-xhr-uids'),

    url(r'^xhr/units/?$',
        views.get_units,
        name='pootle-xhr-units'),
    url(r'^xhr/units/(?P<uid>[0-9]+)/?$',
        views.submit,
        name='pootle-xhr-units-submit'),
    url(r'^xhr/units/(?P<uid>[0-9]+)/comment/?$',
        views.comment,
        name='pootle-xhr-units-comment'),
    url(r'^xhr/units/(?P<uid>[0-9]+)/context/?$',
        views.get_more_context,
        name='pootle-xhr-units-context'),
    url(r'^xhr/units/(?P<uid>[0-9]+)/edit/?$',
        views.UnitEditJSON.as_view(),
        name='pootle-xhr-units-edit'),
    url(r'^xhr/units/(?P<uid>[0-9]+)/timeline/?$',
        views.UnitTimelineJSON.as_view(),
        name='pootle-xhr-units-timeline'),

    url(r'^xhr/units/(?P<uid>[0-9]+)/suggestions/?$',
        views.suggest,
        name='pootle-xhr-units-suggest'),
    url(r'^xhr/units/(?P<uid>[0-9]+)/suggestions/(?P<sugg_id>[0-9]+)/?$',
        views.manage_suggestion,
        name='pootle-xhr-units-suggest-manage'),

    url(r'^xhr/units/(?P<uid>[0-9]+)/checks/(?P<check_id>[0-9]+)/toggle/?$',
        views.toggle_qualitycheck,
        name='pootle-xhr-units-checks-toggle'),
]
