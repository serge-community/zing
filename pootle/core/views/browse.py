# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.functional import cached_property

from pootle.core.browser import get_table_headings
from pootle.core.helpers import (SIDEBAR_COOKIE_NAME,
                                 get_sidebar_announcements_context)
from pootle.core.url_helpers import split_pootle_path
from pootle.core.utils.json import (clean_dict)
from pootle.core.utils.stats import (TOP_CONTRIBUTORS_CHUNK_SIZE,
                                     get_top_scorers_data,
                                     get_translation_states)
from pootle_misc.checks import get_qualitycheck_list

from .base import PootleDetailView


class PootleBrowseView(PootleDetailView):
    template_name = 'browser/index.html'
    table_id = None
    table_fields = None
    items = None
    is_store = False

    @property
    def path(self):
        return self.request.path

    @property
    def stats(self):
        return self.object.get_stats()

    @cached_property
    def cookie_data(self):
        ctx_, cookie_data = self.sidebar_announcements
        return cookie_data

    @property
    def sidebar_announcements(self):
        return get_sidebar_announcements_context(
            self.request,
            (self.object, ))

    @property
    def table(self):
        if self.table_id and self.table_fields and self.items:
            return {
                'id': self.table_id,
                'fields': self.table_fields,
                'headings': get_table_headings(self.table_fields),
            }

    def get(self, *args, **kwargs):
        response = super(PootleBrowseView, self).get(*args, **kwargs)
        if self.cookie_data:
            response.set_cookie(SIDEBAR_COOKIE_NAME, self.cookie_data)
        return response

    def get_context_data(self, *args, **kwargs):
        filters = {}
        can_translate = False
        can_translate_stats = False
        User = get_user_model()

        if self.request.user.is_superuser or self.language:
            can_translate = True
            can_translate_stats = True
            url_action_continue = self.object.get_translate_url(
                state='incomplete',
                **filters)
            url_action_fixcritical = self.object.get_critical_url(
                **filters)
            url_action_review = self.object.get_translate_url(
                state='suggestions',
                **filters)
            url_action_view_all = self.object.get_translate_url(state='all')
        else:
            if self.project:
                can_translate = True
            url_action_continue = None
            url_action_fixcritical = None
            url_action_review = None
            url_action_view_all = None
        ctx, cookie_data_ = self.sidebar_announcements
        ctx.update(super(PootleBrowseView, self).get_context_data(*args, **kwargs))

        lang_code, proj_code = split_pootle_path(self.pootle_path)[:2]
        top_scorers = User.top_scorers(
            project=proj_code,
            language=lang_code,
            limit=TOP_CONTRIBUTORS_CHUNK_SIZE + 1,
        )

        # get stats and top scorers
        stats = self.stats
        top_scorers = get_top_scorers_data(
            top_scorers,
            TOP_CONTRIBUTORS_CHUNK_SIZE)

        # === BEGIN DATA REARRANGEMENT ===
        # TODO: generate data in the proper format without combining

        # expand stats with the additional metadata from self.items
        if self.items:
            for i in self.items:
                code = i['code']
                st = None
                if code not in stats['children']:
                    stats['children'][code] = st
                else:
                    st = stats['children'][code]
                st['title'] = i['title']
                st['is_disabled'] = i['is_disabled']
                st['pootle_path'] = i['href']
                # TODO: refactor original code so that it returns tree item type in a numeric form
                # project = 2, folder = 1, default (file) = 0
                st['treeitem_type'] = \
                    (i['icon'] == 'project') * 2 + \
                    (i['icon'] == 'folder') * 1;

        # get rid of the lastupdated object in children entries
        # (convert it to timestamp, as this is all we need)
        for key in stats['children'].keys():
            i = stats['children'][key]
            if 'lastupdated' in i:
                if i['lastupdated'] is not None and 'creation_time' in i['lastupdated']:
                    i['lastupdated'] = i['lastupdated']['creation_time']
                else:
                    del i['lastupdated']

        # convert children into a list
        # (because we don't need artificial dict keys)
        stats['children'] = stats['children'].values()

        # === END DATA REARRANGEMENT ===

        ctx.update(
            {'page': 'browse',
             'stats_refresh_attempts_count':
                 settings.POOTLE_STATS_REFRESH_ATTEMPTS_COUNT,
             'stats': clean_dict(stats),
             'translation_states': get_translation_states(self.object),
             'checks': get_qualitycheck_list(self.object),
             'can_translate': can_translate,
             'can_translate_stats': can_translate_stats,
             'url_action_continue': url_action_continue,
             'url_action_fixcritical': url_action_fixcritical,
             'url_action_review': url_action_review,
             'url_action_view_all': url_action_view_all,
             'table': self.table,
             'is_store': self.is_store,
             'top_scorers': clean_dict(top_scorers),
             'browser_extends': self.template_extends})

        return ctx
