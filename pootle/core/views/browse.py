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
from django.http import Http404
from django.utils.functional import cached_property

from pootle.core.helpers import (SIDEBAR_COOKIE_NAME,
                                 get_sidebar_announcements_context)
from pootle.core.url_helpers import split_pootle_path
from pootle.core.utils.json import remove_empty_from_dict
from pootle.core.utils.stats import (TOP_CONTRIBUTORS_CHUNK_SIZE,
                                     get_top_scorers_data,
                                     get_translation_states)
from pootle_app.models.permissions import check_user_permission
from pootle_misc.checks import get_qualitycheck_list

from ..http import JsonResponse
from .base import PootleDetailView


class BrowseDataViewMixin(object):

    @cached_property
    def items(self):
        return self.object.children

    @cached_property
    def stats(self):
        return self.object.get_stats()

    def get_item_data(self, path_obj, stats):
        """Shapes `path_obj` to be an item usable in the browsing table row.

        :param path_obj: Element to retrieve row information for. This can
            either be a `Project`, `Language`, `Directory` or `Store`.
        :param stats: Dictionary containing stats for this particular
            `path_obj`.
        """
        return (path_obj.pootle_path, {
            # FIXME: rename to `type`
            'treeitem_type': self.get_item_type(path_obj),
            'title': self.get_item_title(path_obj),
            'is_disabled': getattr(path_obj, 'disabled', False),

            'total': stats.get('total', 0),
            'translated': stats.get('translated', 0),
            'fuzzy': stats.get('fuzzy', 0),
            'critical': stats.get('critical', 0),
            'suggestions': stats.get('suggestions', 0),
            'lastaction': stats.get('lastaction', 0),
            'lastupdated': stats.get('lastupdated', 0),
        })

    def get_browsing_data(self):
        browsing_data = remove_empty_from_dict({
            key: value
            for key, value in self.stats.iteritems()
            if key != 'children'
        })

        has_admin_access = check_user_permission(self.request.user,
                                                 'administrate',
                                                 self.permission_context)
        if 'total' not in browsing_data and not has_admin_access:
            raise Http404

        children_stats = self.stats['children']
        browsing_data.update({
            'children': {
                path: remove_empty_from_dict(data)
                for path, data in (
                    self.get_item_data(item, children_stats[i])
                    for i, item in enumerate(self.items)
                ) if data['total'] > 0 or has_admin_access
            },
        })
        return browsing_data


class PootleBrowseView(BrowseDataViewMixin, PootleDetailView):
    template_name = 'browser/index.html'

    @property
    def path(self):
        return self.request.path

    @cached_property
    def cookie_data(self):
        ctx_, cookie_data = self.sidebar_announcements
        return cookie_data

    @property
    def sidebar_announcements(self):
        return get_sidebar_announcements_context(self.request, (self.object,))

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
            url_action_fixcritical = self.object.get_translate_url(
                check_category='critical',
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
        top_scorers = get_top_scorers_data(top_scorers,
                                           TOP_CONTRIBUTORS_CHUNK_SIZE)

        ctx.update({
            'page': 'browse',
            'stats_refresh_attempts_count':
                settings.POOTLE_STATS_REFRESH_ATTEMPTS_COUNT,
            'browsing_data': self.get_browsing_data(),
            'translation_states': get_translation_states(self.object),
            'checks': get_qualitycheck_list(self.object),
            'can_translate': can_translate,
            'can_translate_stats': can_translate_stats,
            'url_action_continue': url_action_continue,
            'url_action_fixcritical': url_action_fixcritical,
            'url_action_review': url_action_review,
            'url_action_view_all': url_action_view_all,
            'top_scorers': remove_empty_from_dict(top_scorers),
            'browser_extends': self.template_extends,
        })

        return ctx


class BaseBrowseDataJSON(BrowseDataViewMixin):

    @property
    def path(self):
        return self.kwargs['path']

    def get_context_data(self, *args, **kwargs):
        return self.get_browsing_data()

    def render_to_response(self, context, **kwargs):
        return JsonResponse(context)
