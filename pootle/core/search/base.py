# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from django.conf import settings


class SearchBackend(object):
    def __init__(self):
        self._settings = getattr(settings, "ZING_TM_SERVER", None)

    def search(self, unit):
        """Search for TM results.

        :param unit: :cls:`~pootle_store.models.Unit`
        :return: list of results or [] for no results or offline
        """
        raise NotImplementedError

    def update(self, language, obj):
        """Add a unit to the backend"""
        pass
