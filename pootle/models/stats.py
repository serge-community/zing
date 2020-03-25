# -*- coding: utf-8 -*-
#
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import logging

from django.utils.encoding import iri_to_uri

from pootle.core.cache import get_cache
from pootle.core.mixins.treeitem import CachedMethods


logger = logging.getLogger("stats")
cache = get_cache("stats")


class Stats(object):
    """Retrieves stats directly from the cache.

    This is a basic, standalone, and lightweight version of the implementation
    available in `CachedTreeItem` and is limited to paths which mixin with this
    class. It also doesn't account for children stats.
    """

    def __init__(self, path, *args, **kwargs):
        self.path = path

    @property
    def total(self):
        return self.get_wordcount()["total"]

    @property
    def translated(self):
        return self.get_wordcount()["translated"]

    @property
    def fuzzy(self):
        return self.get_wordcount()["fuzzy"]

    @property
    def incomplete(self):
        try:
            return self.total - self.translated
        except TypeError:
            return None

    @property
    def critical(self):
        check_stats = self.get_value(CachedMethods.CHECKS, {})
        return check_stats.get("unit_critical_error_count", None)

    @property
    def suggestions(self):
        return self.get_value(CachedMethods.SUGGESTIONS)

    @property
    def last_action(self):
        return self.get_value(CachedMethods.LAST_ACTION)

    @property
    def last_updated(self):
        return self.get_value(CachedMethods.LAST_UPDATED)

    def make_cache_key(self, name):
        return iri_to_uri("%s:%s" % (self.path, name))

    def get_value(self, name, default=None):
        """get stat value from cache"""
        key = self.make_cache_key(name)
        result = cache.get(key)
        if result is None:
            logger.debug(u"Cache miss %s for %s", name, key)
            return default

        return result

    def get_wordcount(self):
        return self.get_value(
            CachedMethods.WORDCOUNT_STATS,
            {"total": None, "translated": None, "fuzzy": None},
        )
