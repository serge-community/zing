# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from django.db.models import Max
from django.utils.functional import cached_property

from pootle_store.constants import SIMPLY_SORTED
from pootle_store.models import Unit
from pootle_store.unit.filters import UnitSearchFilter, UnitTextSearch


class DBSearchBackend(object):

    default_chunk_size = None
    default_order = "store__pootle_path", "index"
    select_related = (
        'store__translation_project__project',
        'store__translation_project__language')

    def __init__(self, request_user, **kwargs):
        self.kwargs = kwargs
        self.request_user = request_user

    @property
    def chunk_size(self):
        return self.kwargs.get(
            'count',
            self.default_chunk_size)

    @property
    def project_code(self):
        return self.kwargs.get("project_code")

    @property
    def language_code(self):
        return self.kwargs.get("language_code")

    @property
    def dir_path(self):
        return self.kwargs.get("dir_path")

    @property
    def filename(self):
        return self.kwargs.get("filename")

    @property
    def unit_filter(self):
        return self.kwargs.get("filter")

    @property
    def offset(self):
        return self.kwargs.get("offset", None)

    @property
    def previous_uids(self):
        return self.kwargs.get("previous_uids", []) or []

    @property
    def sort_by(self):
        return self.kwargs.get("sort_by")

    @property
    def sort_on(self):
        return self.kwargs.get("sort_on")

    @property
    def uid(self):
        return self.kwargs.get("uid")

    @property
    def uids(self):
        return self.kwargs.get("uids", [])

    @property
    def units_qs(self):
        kwargs = {
            'project_code': self.project_code,
            'language_code': self.language_code,
            'dir_path': self.dir_path,
            'filename': self.filename,
            'user': self.request_user,
        }
        return (
            Unit.objects.get_translatable(**kwargs)
                        .order_by(*self.default_order)
                        .select_related(*self.select_related)
        )

    def sort_qs(self, qs):
        if self.unit_filter and self.sort_by is not None:
            sort_by = self.sort_by
            if self.sort_on not in SIMPLY_SORTED:
                # Omit leading `-` sign
                if self.sort_by[0] == '-':
                    max_field = self.sort_by[1:]
                    sort_by = '-sort_by_field'
                else:
                    max_field = self.sort_by
                    sort_by = 'sort_by_field'
                # It's necessary to use `Max()` here because we can't
                # use `distinct()` and `order_by()` at the same time
                qs = qs.annotate(sort_by_field=Max(max_field))
            return qs.order_by(
                sort_by, "store__pootle_path", "index")
        return qs

    def filter_qs(self, qs, uid_list=None):
        kwargs = self.kwargs
        category = kwargs['category']
        checks = kwargs['checks']
        exact = 'exact' in kwargs['soptions']
        modified_since = kwargs['modified-since']
        month = kwargs['month']
        search = kwargs['search']
        sfields = kwargs['sfields']
        user = kwargs['user']

        if self.unit_filter:
            qs = UnitSearchFilter().filter(
                qs, self.unit_filter,
                user=user, checks=checks, category=category)

            if modified_since is not None:
                qs = qs.filter(
                    submitted_on__gt=modified_since).distinct()

            if month is not None:
                qs = qs.filter(
                    submitted_on__gte=month[0],
                    submitted_on__lte=month[1]).distinct()

        if sfields and search:
            qs = UnitTextSearch(qs).search(
                search, sfields, exact=exact)
        return qs

    @cached_property
    def results(self):
        return self.sort_qs(self.filter_qs(self.units_qs))

    def get_uids(self):
        MAX_RESULTS = 1000 # TODO: move to some config?

        total = self.results.count()

        begin = 0
        end = min(MAX_RESULTS, total)

        uids = None

        # if there are more results than MAX_RESULTS,
        # and if we're requesting a specific unit
        # in a specific store, adjust the results window
        # so that the requested unit is in the middle

        if (total > MAX_RESULTS
            and self.language_code
            and self.project_code
            and self.filename
            and self.uid):
            # find the uid in the Store
            uid_list = list(self.results.values_list("pk", flat=True))
            if self.uid in uid_list:
                begin = max(uid_list.index(self.uid) - MAX_RESULTS / 2, 0)
                end = min(begin + MAX_RESULTS, total)
                uids = uid_list[begin:end]

        if not uids:
            uids = list(self.results[begin:end].values_list("pk", flat=True))
        return begin, end, total, uids

    def get_view_rows(self):
        if not self.uids:
            raise ValueError('No uids provided')

        return self.units_qs.filter(id__in=self.uids)
