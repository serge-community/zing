# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import logging

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.functional import cached_property

from pootle.core.log import log
from pootle.core.models import Revision

from .constants import OBSOLETE, PARSED
from .diff import StoreDiff
from .util import get_change_str


class StoreUpdate(object):
    """Wraps either a db or file store with instructions for updating
    a target db store
    """

    def __init__(self, source_store, **kwargs):
        self.source_store = source_store
        self.kwargs = kwargs

    def find_source_unit(self, uid):
        return self.source_store.findid(uid)

    def get_index(self, uid):
        return self.indices[uid]['index']

    @property
    def uids(self):
        return list(self.kwargs["uids"])

    @property
    def indices(self):
        return self.kwargs["indices"]

    @property
    def store_revision(self):
        return self.kwargs["store_revision"]

    @property
    def submission_type(self):
        return self.kwargs["submission_type"]

    @property
    def update_revision(self):
        return self.kwargs["update_revision"]

    @property
    def user(self):
        return self.kwargs["user"]

    @property
    def suggest_on_conflict(self):
        return self.kwargs.get("suggest_on_conflict", True)


class FrozenUnit(object):
    """Freeze unit vars for comparison"""

    def __init__(self, unit):
        self.target = unit.target_f
        self.state = unit.state
        self.submitter = unit.submitted_by
        self.translator_comment = unit.getnotes(origin="translator")


class UnitUpdater(object):
    """Updates a unit from a source with configuration"""

    def __init__(self, unit, update):
        self.unit = unit
        self.update = update
        self.original = FrozenUnit(unit)

    @property
    def translator_comment(self):
        return self.unit.getnotes(origin="translator")

    @property
    def translator_comment_updated(self):
        return (
            (self.original.translator_comment or self.translator_comment)
            and self.original.translator_comment != self.translator_comment)

    @cached_property
    def at(self):
        return timezone.now()

    @property
    def uid(self):
        return self.unit.getid()

    @cached_property
    def newunit(self):
        return self.update.find_source_unit(self.uid)

    @cached_property
    def conflict_found(self):
        """Determines whether a conflict has been found or not.

        A conflict is found when:
          - there were changes in the DB since the last sync
          - source or target texts differ between the file and the DB units
        """
        return (
            self.newunit
            and self.update.store_revision is not None
            and self.update.store_revision < self.unit.revision
            and (self.unit.target != self.newunit.target
                 or self.unit.source != self.newunit.source)
        )

    @property
    def should_create_suggestion(self):
        return self.update.suggest_on_conflict and self.conflict_found

    @property
    def should_update_index(self):
        return (
            self.uid in self.update.indices
            and self.unit.index != self.update.get_index(self.uid)
        )

    @property
    def should_merge(self):
        """Determines whether the new unit from the file needs to be
        merged with the existing DB unit.

        Merging considers source, target, comment and state changes.
        """
        return self.newunit and not self.conflict_found

    @property
    def should_resurrect(self):
        """Determines whether the existing DB unit needs to be resurrected
        because:
            1. it was obsolete (but the new unit is not), and
            2. it contained unsynced changes.
        """
        return (
            self.unit.isobsolete()
            and not self.newunit.isobsolete()
            and self.unit.revision > self.update.store_revision
        )

    @property
    def target_updated(self):
        return self.unit.target != self.original.target

    def create_suggestion(self):
        return bool(
            self.unit.add_suggestion(self.newunit.target, self.update.user)[1]
        )

    def save_unit(self):
        """Saves the updated unit to the DB.

        The method takes care of recording submissions as well as setting
        values for denormalized fields.
        """
        self.unit.store.record_submissions(
            self.unit,
            self.original.target,
            self.original.state,
            self.at,
            self.update.user,
            self.update.submission_type,
        )

        if self.translator_comment_updated:
            self.unit.commented_by = self.update.user
            self.unit.commented_on = self.at

        if self.target_updated:
            self.unit.submitted_by = self.update.user
            self.unit.submitted_on = self.at
            self.unit.reviewed_on = None
            self.unit.reviewed_by = None

        self.unit.save(revision=self.update.update_revision)

    def update_unit(self):
        """Updates the current `self.unit` in the DB.

        This method serves as a layer above the unit-level update logic to
        enhance it with conflict resolution.

        :return: (updated, suggested, unsynced) a tuple of booleans:
            updated: whether an update to the unit was performed and saved .
            suggested: whether a suggestion was added due to conflicts.
            unsynced: whether an obsolete unit was resurrected because it
                contained unsynced changes.
        """
        suggested = False
        updated = False
        unsynced = False

        if self.should_merge:
            updated = self.unit.update(self.newunit, user=self.update.user)
        elif self.should_resurrect:
            updated = self.unit.resurrect(is_fuzzy=self.unit.isfuzzy())
            unsynced = updated

        if self.should_update_index:
            self.unit.index = self.update.get_index(self.uid)
            updated = True

        if updated:
            self.save_unit()

        if self.should_create_suggestion:
            suggested = self.create_suggestion()

        return updated, suggested, unsynced


class StoreUpdater(object):

    def __init__(self, target_store):
        self.target_store = target_store

    def get_unsynced_uids(self, update_revision):
        return self.target_store.unit_set.filter(
            revision__gt=self.target_store.last_sync_revision,
            revision__lt=update_revision,
            state__gt=OBSOLETE,
        ).values_list('id', flat=True)

    def incr_unit_revision(self, uid_list):
        """Increments the revision for units within `uid_list`.

        :return: the amount of units for which the revision has been
            incremented.
        """
        if not uid_list:
            return 0

        return self.target_store.unit_set.filter(id__in=uid_list).update(
            revision=Revision.incr()
        )

    def units(self, uids):
        unit_set = self.target_store.unit_set.select_related("submitted_by")
        for unit in self.target_store.findid_bulk(uids, unit_set):
            unit.store = self.target_store
            yield unit

    def update(self, store, user=None, store_revision=None,
               submission_type=None):
        logging.debug(u"Updating %s", self.target_store.pootle_path)
        old_state = self.target_store.state

        if user is None:
            User = get_user_model()
            user = User.objects.get_system_user()

        update_revision = None
        changes = {}
        unsynced_uids = []
        try:
            diff = StoreDiff(self.target_store, store, store_revision).diff()
            if diff is not None:
                update_revision = Revision.incr()
                changes, unsynced_uids = self.update_from_diff(
                    store,
                    store_revision,
                    diff, update_revision,
                    user, submission_type,
                )
        finally:
            if old_state < PARSED:
                self.target_store.state = PARSED
            else:
                self.target_store.state = old_state
            has_changed = any(x > 0 for x in changes.values())
            self.target_store.save(update_cache=has_changed)
            if has_changed:
                log(u"[update] %s units in %s [revision: %d]"
                    % (get_change_str(changes),
                       self.target_store.pootle_path,
                       self.target_store.get_max_unit_revision()))

        return update_revision, changes, unsynced_uids

    def update_from_diff(self, store, store_revision,
                         to_change, update_revision, user,
                         submission_type):
        changes = {}

        # Update indexes
        for start, delta in to_change["index"]:
            self.target_store.update_index(start=start, delta=delta)

        # Add new units
        for unit, new_unit_index in to_change["add"]:
            self.target_store.addunit(
                unit, new_unit_index, user=user,
                update_revision=update_revision,
            )
        changes["added"] = len(to_change["add"])

        # Obsolete units
        changes["obsoleted"] = self.target_store.mark_units_obsolete(
            to_change["obsolete"], update_revision,
        )

        # Update units
        update_dbids, uid_index_map = to_change['update']
        update = StoreUpdate(
            store,
            user=user,
            submission_type=submission_type,
            uids=update_dbids,
            indices=uid_index_map,
            store_revision=store_revision,
            update_revision=update_revision,
        )
        updated, suggested, unsynced_uids = self.update_units(update)
        changes.update({
            'updated': updated,
            'suggested': suggested,
        })
        return changes, unsynced_uids

    def update_from_disk(self, overwrite=False):
        """Update DB with units from the disk file.

        :param overwrite: process all units from the file regardless of
            `last_sync_revision`.
        :return: boolean, whether the DB store has been changed or not.
        """
        if not self.target_store.file:
            return False

        if overwrite:
            store_revision = self.target_store.get_max_unit_revision()
        else:
            store_revision = self.target_store.last_sync_revision or 0

        # update the units
        update_revision, changes, unsynced_uids = self.update(
            self.target_store.file.store,
            store_revision=store_revision)

        # update file_mtime
        self.target_store.file_mtime = self.target_store.get_file_mtime()

        # update last_sync_revision if anything changed
        changed = changes and any(x > 0 for x in changes.values())
        if not changed:
            self.target_store.save(update_cache=False)  # Saves mtime
            return False

        if self.target_store.last_sync_revision is not None:
            unsynced_uids += list(self.get_unsynced_uids(update_revision))
            unsynced_count = self.incr_unit_revision(unsynced_uids)
            if unsynced_count:
                logging.info(
                    u'[update] unsynced %d units in %s [revision: %d]',
                    unsynced_count, self.target_store.pootle_path,
                    update_revision,
                )

        self.target_store.last_sync_revision = update_revision
        self.target_store.save(update_cache=False)

        return True

    def update_units(self, update):
        """Update individual DB units via `UnitUpdater`.

        The specific units that need to go through the update are
        specificed in the `update` configuraton's `uids` property.
        These were previously calculated via a diff retrieved from
        `StoreDiff().diff()`.

        :param update: the update configuration, an instance of `StoreUpdate`.
        :return: tuple of (update_count, suggestion_count, unsynced_uids):
            update_count: the amount of updates performed.
            suggestion_count: the amount of suggestions added.
            unsynced_uids: list of ids of units that were resurrected
                but are unsynced.
        """
        update_count = 0
        suggestion_count = 0
        unsynced_uids = []

        for unit in self.units(update.uids):
            updated, suggested, unsynced = (
                UnitUpdater(unit, update).update_unit()
            )
            if updated:
                update_count += 1
            if suggested:
                suggestion_count += 1
            if unsynced:
                unsynced_uids.append(unit.id)

        return update_count, suggestion_count, unsynced_uids
