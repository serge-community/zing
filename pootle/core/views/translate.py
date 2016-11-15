# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from django.conf import settings

from pootle.core.url_helpers import get_previous_url
from pootle_app.models.permissions import check_permission
from pootle_misc.checks import get_qualitycheck_schema
from pootle_misc.forms import make_search_form

from .base import PootleDetailView


class PootleTranslateView(PootleDetailView):
    template_name = "editor/main.html"

    @property
    def ctx_path(self):
        return self.pootle_path

    def get_context_data(self, *args, **kwargs):
        ctx = super(PootleTranslateView, self).get_context_data(*args, **kwargs)
        ctx.update({
            'page': 'translate',
            'ctx_path': self.ctx_path,
            'check_categories': get_qualitycheck_schema(),
            'cantranslate': check_permission("translate", self.request),
            'cansuggest': check_permission("suggest", self.request),
            'canreview': check_permission("review", self.request),
            'search_form': make_search_form(request=self.request),
            'previous_url': get_previous_url(self.request),
            'POOTLE_MT_BACKENDS': settings.POOTLE_MT_BACKENDS,
            'editor_extends': self.template_extends,
        })
        return ctx
