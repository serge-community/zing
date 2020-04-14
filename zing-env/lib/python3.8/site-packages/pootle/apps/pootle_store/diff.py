# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import difflib
from collections import OrderedDict

from django.db import models
from django.utils.functional import cached_property

from .constants import FUZZY, OBSOLETE, TRANSLATED, UNTRANSLATED
from .fields import to_python as multistring_to_python
from .unit import UnitProxy


class UnitDiffProxy(UnitProxy):
    """Wraps File/DB Unit dicts used by StoreDiff for equality comparison"""

    match_attrs = [
        "context",
        "developer_comment",
        "locations",
        "source",
        "state",
        "target",
        "translator_comment",
    ]

    def __eq__(self, other):
        return all(getattr(self, k) == getattr(other, k) for k in self.match_attrs)

    def __ne__(self, other):
        return not self == other


class DBUnit(UnitDiffProxy):
    pass


class FileUnit(UnitDiffProxy):
    @property
    def locations(self):
        return "\n".join(self.unit["locations"])

    @property
    def source(self):
        return multistring_to_python(self.unit["source"])

    @property
    def target(self):
        return multistring_to_python(self.unit["target"])


class FileStore(object):
    """File store representation for diffing."""

    def __init__(self, store):
        self.store = store

    @cached_property
    def units(self):
        """Returns all file units except the header."""
        return OrderedDict(
            (unit.getid(), self.get_file_unit(unit))
            for unit in self.store.units
            if not unit.isheader()
        )

    def get_file_unit(self, unit):
        """Retrieves individual unit data.

        The method maps file unit's state to DB state values for comparison.
        :param unit: a TTK `Unit`.
        """
        state = UNTRANSLATED
        if unit.isobsolete():
            state = OBSOLETE
        elif unit.istranslated():
            state = TRANSLATED
        elif unit.isfuzzy():
            state = FUZZY

        return {
            "unitid": unit.getid(),
            "context": unit.getcontext(),
            "locations": unit.getlocations(),
            "source": unit.source,
            "target": unit.target,
            "state": state,
            "developer_comment": unit.getnotes(origin="developer"),
            "translator_comment": unit.getnotes(origin="translator"),
        }

    def get_unit(self, id):
        """Retrieves a comparable `FileUnit` object by `id`."""
        return FileUnit(self.units[id])


class DBStore(object):
    """DB store representation for diffing.

    :param store: the DB store to wrap
    :param only_active: whether to consider active units only
        (i.e. filter out obsolete units)
    """

    unit_fields = (
        "unitid",
        "state",
        "id",
        "index",
        "revision",
        "source_f",
        "target_f",
        "developer_comment",
        "translator_comment",
        "locations",
        "context",
    )

    def __init__(self, store, only_active=False):
        self.store = store
        self.only_active = only_active

    @cached_property
    def units(self):
        """Returns all DB units regardless of their state or revision."""
        qs = self.store.unit_set
        if self.only_active:
            qs = qs.live()
        units = qs.values(*self.unit_fields).order_by("index")
        return OrderedDict((unit["unitid"], unit) for unit in units)

    @cached_property
    def active_uids(self):
        return [uid for uid, unit in self.units.items() if unit["state"] != OBSOLETE]

    def get_unit(self, id):
        """Retrieves a comparable `DBUnit` object by `id`."""
        return DBUnit(self.units[id])

    def get_updated_uids(self, since_revision):
        """Return a list of *active* unit IDs that were updated since
        `since_revision` revision.
        """
        return [
            uid
            for uid, unit in self.units.items()
            if (unit["revision"] > since_revision and unit["state"] != OBSOLETE)
        ]


class StoreDiff(object):
    """Compares a file and DB store.

    Throughout this class, `source` always refers to a file store, whereas
    `target` refers to a DB store.
    """

    def __init__(self, target_store, source_store, source_revision):
        self.target_store = target_store
        self.target_revision = self.target_store.get_max_unit_revision()
        self.source_store = source_store
        self.source_revision = source_revision or -1

    @cached_property
    def source(self):
        if isinstance(self.source_store, models.Model):
            return DBStore(self.source_store, only_active=True)
        return FileStore(self.source_store)

    @cached_property
    def target(self):
        return DBStore(self.target_store)

    @cached_property
    def insert_points(self):
        """Returns a list of insert points with update index info.

        :return: a list of tuples
            `(insert_at, uids_to_add, next_index, update_index_delta)` where
                * `insert_at` is the point for inserting,
                * `uids_to_add` are the units to be inserted,
                * `next_index` is the starting point after which
                    `update_index_delta` should be applied,
                * `update_index_delta` is the offset for index updating.
        """
        inserts = []
        new_unitid_list = self.new_unit_list
        units = self.target.units
        active_uids = self.target.active_uids

        for (tag, i1, i2, j1, j2) in self.opcodes:
            if tag == "insert":
                update_index_delta = 0
                insert_at = 0
                if i1 > 0:
                    insert_at = units[active_uids[i1 - 1]]["index"]

                next_index = insert_at + 1
                if i1 < len(active_uids):
                    next_index = units[active_uids[i1]]["index"]
                    update_index_delta = j2 - j1 - next_index + insert_at + 1

                inserts.append(
                    (insert_at, new_unitid_list[j1:j2], next_index, update_index_delta,)
                )

            elif tag == "replace":
                insert_at = units[active_uids[i1 - 1]]["index"]
                next_index = units[active_uids[i2 - 1]]["index"]
                inserts.append(
                    (
                        insert_at,
                        new_unitid_list[j1:j2],
                        next_index,
                        j2 - j1 - insert_at + next_index,
                    )
                )

        return inserts

    @cached_property
    def new_unit_list(self):
        # If source_revision is gte than the target_revision then new unit list
        # will be exactly what is in the file
        if self.source_revision >= self.target_revision:
            return list(self.source.units.keys())

        # These units are kept as they have been updated since source_revision
        # but do not appear in the file
        new_units = [u for u in self.updated_target_units if u not in self.source.units]

        # These units are either present in both or only in the file so are
        # kept in the file order
        new_units += list(self.source.units.keys())

        return new_units

    @cached_property
    def updated_target_units(self):
        return self.target.get_updated_uids(since_revision=self.source_revision)

    @cached_property
    def opcodes(self):
        sm = difflib.SequenceMatcher(None, self.target.active_uids, self.new_unit_list)
        return sm.get_opcodes()

    def diff(self):
        """Return a dictionary of change actions or None if there are no
        changes to be made.
        """
        diff = {
            "index": self.get_indexes_to_update(),
            "obsolete": self.get_units_to_obsolete(),
            "add": self.get_units_to_add(),
            "update": self.get_units_to_update(),
        }
        if self.has_changes(diff):
            return diff
        return None

    def get_indexes_to_update(self):
        offset = 0
        index_updates = []
        for (insert_at_, uids_add_, next_index, delta) in self.insert_points:
            if delta > 0:
                index_updates += [(next_index + offset, delta)]
                offset += delta
        return index_updates

    def get_units_to_add(self):
        offset = 0
        to_add = []
        for (insert_at, uids_add, next_index_, delta) in self.insert_points:
            for index, uid in enumerate(uids_add):
                source_unit = self.source_store.findid(uid)
                if source_unit and source_unit.getid() not in self.target.units:
                    new_unit_index = insert_at + index + 1 + offset
                    to_add += [(source_unit, new_unit_index)]
            if delta > 0:
                offset += delta
        return to_add

    def get_units_to_obsolete(self):
        return [
            unit["id"]
            for unitid, unit in self.target.units.items()
            if (
                unitid not in self.source.units
                and unitid in self.target.active_uids
                and unitid not in self.updated_target_units
            )
        ]

    def get_units_to_update(self):
        uid_index_map = {}
        offset = 0

        for (insert_at, uids_add, next_index_, delta) in self.insert_points:
            for index, uid in enumerate(uids_add):
                new_unit_index = insert_at + index + 1 + offset
                if uid in self.target.units:
                    uid_index_map[uid] = {
                        "dbid": self.target.units[uid]["id"],
                        "index": new_unit_index,
                    }
            if delta > 0:
                offset += delta
        update_ids = self.get_updated_sourceids()
        update_ids.update({x["dbid"] for x in uid_index_map.values()})
        return (update_ids, uid_index_map)

    def get_updated_sourceids(self):
        """Returns a set of unit DB ids to be updated.
        """
        update_ids = set()

        for (tag, i1, i2, j1_, j2_) in self.opcodes:
            if tag != "equal":
                continue

            update_ids.update(
                set(
                    self.target.units[uid]["id"]
                    for uid in self.target.active_uids[i1:i2]
                    if (
                        uid in self.source.units
                        and self.source.get_unit(uid) != self.target.get_unit(uid)
                    )
                )
            )

        return update_ids

    def has_changes(self, diff):
        for k, v in diff.items():
            if k == "update":
                if len(v[0]) > 0:
                    return True
            else:
                if len(v) > 0:
                    return True
        return False
