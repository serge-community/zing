# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import io
import os

import pytest

from pytest_pootle.factories import (LanguageDBFactory, StoreDBFactory,
                                     TranslationProjectFactory)

from translate.storage.factory import getclass

from django.core.exceptions import ValidationError

from pootle.core.models import Revision
from pootle.core.url_helpers import to_tp_relative_path
from pootle_store.constants import OBSOLETE, PARSED, TRANSLATED
from pootle_store.diff import StoreDiff
from pootle_store.models import Store
from pootle_store.syncer import PoStoreSyncer


@pytest.mark.django_db
def test_delete_mark_obsolete(project0_disk, store0):
    """Tests that the in-DB Store and Directory are marked as obsolete
    after the on-disk file ceased to exist.

    Refs. #269.
    """
    tp = TranslationProjectFactory(
        project=project0_disk, language=LanguageDBFactory()
    )
    store = StoreDBFactory(translation_project=tp, parent=tp.directory)

    store.update(store.deserialize(store0.serialize()))
    store.sync()
    pootle_path = store.pootle_path

    # Remove on-disk file
    os.remove(store.file.path)

    # Update stores by rescanning TP
    tp.scan_files()

    # Now files that ceased to exist should be marked as obsolete
    updated_store = Store.objects.get(pootle_path=pootle_path)
    assert updated_store.obsolete

    # The units they contained are obsolete too
    assert not updated_store.units.exists()
    assert updated_store.unit_set.filter(state=OBSOLETE).exists()


@pytest.mark.django_db
def test_sync(project0_disk, store0):
    """Tests that the new on-disk file is created after sync for existing
    in-DB Store if the corresponding on-disk file ceased to exist.
    """
    tp = TranslationProjectFactory(
        project=project0_disk, language=LanguageDBFactory()
    )
    store = StoreDBFactory(translation_project=tp, parent=tp.directory)

    store.update(store.deserialize(store0.serialize()))
    assert not store.file.exists()
    store.sync()
    assert store.file.exists()
    os.remove(store.file.path)
    assert not store.file.exists()
    store.sync()
    assert store.file.exists()


@pytest.mark.django_db
def test_update_with_non_ascii(store0, test_fs):
    store0.state = PARSED
    orig_units = store0.units.count()
    with test_fs.open(['data', 'po', 'tutorial', 'en',
                       'tutorial_non_ascii.po']) as f:
        store = getclass(f)(f.read())
    store0.update(store)
    assert store0.units[orig_units].target == "Hèḽḽě, ŵôrḽḓ"


@pytest.mark.django_db
def test_update_unit_order(project0_disk, ordered_po, ordered_update_ttk):
    """Tests unit order after a specific update.
    """

    # Set last sync revision
    ordered_po.sync()
    assert ordered_po.file.exists()

    old_unit_list = ['1->2', '2->4', '3->3', '4->5']
    updated_unit_list = list(
        [unit.unitid for unit in ordered_po.units]
    )
    assert old_unit_list == updated_unit_list
    current_revision = ordered_po.get_max_unit_revision()

    ordered_po.update(
        ordered_update_ttk,
        store_revision=current_revision)

    old_unit_list = [
        'X->1', '1->2', '3->3', '2->4',
        '4->5', 'X->6', 'X->7', 'X->8']
    updated_unit_list = list(
        [unit.unitid for unit in ordered_po.units]
    )
    assert old_unit_list == updated_unit_list


@pytest.mark.django_db
def test_update_save_changed_units(project0_disk, store0):
    """Tests that any update saves changed units only.
    """
    store = store0

    # Set last sync revision
    store.sync()

    store.update(store.file.store)
    unit_list = list(store.units)

    store.file = 'tutorial/ru/update_save_changed_units_updated.po'
    store.update(store.file.store)
    updated_unit_list = list(store.units)

    for index in range(0, len(unit_list)):
        unit = unit_list[index]
        updated_unit = updated_unit_list[index]
        if unit.target == updated_unit.target:
            assert unit.revision == updated_unit.revision
            assert unit.mtime == updated_unit.mtime


@pytest.mark.django_db
def test_update_set_last_sync_revision(project0_disk, tp0, store0, test_fs):
    """Tests setting last_sync_revision after store creation."""
    unit = store0.units.first()
    unit.target = "UPDATED TARGET"
    unit.save()

    store0.sync()

    # Store is already parsed and nothing is unsynced
    assert store0.last_sync_revision == store0.get_max_unit_revision()

    # An empty update leaves `last_sync_revision` intact
    saved_last_sync_revision = store0.last_sync_revision
    store0.updater.update_from_disk()
    assert store0.last_sync_revision == saved_last_sync_revision

    orig = str(store0)
    update_file = test_fs.open(
        "data/po/tutorial/ru/update_set_last_sync_revision_updated.po",
        "r")
    with update_file as sourcef:
        with open(store0.file.path, "wb") as targetf:
            targetf.write(sourcef.read())

    # any non-empty update sets last_sync_revision to next global revision
    next_revision = Revision.get() + 1
    store0.updater.update_from_disk()
    assert store0.last_sync_revision == next_revision

    # Make a change to a unit, so that it's unsynced
    next_unit_revision = Revision.get() + 1
    dbunit = store0.units.first()
    dbunit.target = "ANOTHER DB TARGET UPDATE"
    dbunit.save()
    assert dbunit.revision == next_unit_revision

    # After the next empty update, the store's revision remains the same
    store0.updater.update_from_disk()
    assert store0.last_sync_revision == next_revision

    # Now that there are unsynced units, the next non-empty update
    # will set the last sync revision to the next global revision
    next_revision = Revision.get() + 1

    with open(store0.file.path, "wb") as targetf:
        targetf.write(orig)

    store0.updater.update_from_disk()
    assert store0.last_sync_revision == next_revision

    # The unsynced unit's revision should be greater than the last sync
    # revision to allow syncing it after this update
    dbunit = store0.units[0]
    assert dbunit.revision == store0.last_sync_revision + 1


def _test_store_update_indexes(store):
    # make sure indexes are not fooed indexes only have to be unique
    indexes = [x.index for x in store.units]
    assert len(indexes) == len(set(indexes))


def _test_store_update_units_before(store, units_in_file, store_revision,
                                    units_before_update, member2):
    # test what has happened to the units that were present before the update
    updates = {unit[0]: unit[1] for unit in units_in_file}

    for unit in units_before_update:
        updated_unit = store.unit_set.get(unitid=unit.unitid)

        if unit.source not in updates:
            # unit is not in update, target should be left unchanged
            assert updated_unit.target == unit.target
            assert updated_unit.submitted_by == unit.submitted_by

            # depending on unit/store_revision should be obsoleted
            if unit.isobsolete() or store_revision >= unit.revision:
                assert updated_unit.isobsolete()
            else:
                assert not updated_unit.isobsolete()

            continue

        # unit is in update
        if store_revision >= unit.revision:
            assert not updated_unit.isobsolete()
        elif unit.isobsolete():
            # the unit has been obsoleted since store_revision
            assert updated_unit.isobsolete()
        else:
            assert not updated_unit.isobsolete()

        if updated_unit.isobsolete():
            continue

        if store_revision >= unit.revision:
            # file store wins outright
            assert updated_unit.target == updates[unit.source]
            if unit.target != updates[unit.source]:
                # unit has changed
                assert updated_unit.submitted_by == member2

                # damn mysql microsecond precision
                if unit.submitted_on.time().microsecond != 0:
                    assert updated_unit.submitted_on != unit.submitted_on
            else:
                assert updated_unit.submitted_by == unit.submitted_by
                assert updated_unit.submitted_on == unit.submitted_on
            assert updated_unit.get_suggestions().count() == 0

            continue

        # conflict found
        suggestion = updated_unit.get_suggestions()[0]
        assert updated_unit.target == unit.target
        assert updated_unit.submitted_by == unit.submitted_by
        assert suggestion.target == updates[unit.source]
        assert suggestion.user == member2


def _test_store_update_ordering(store, units_in_file, store_revision,
                                units_before_update):
    updates = {unit[0]: unit[1] for unit in units_in_file}
    old_units = {unit.source: unit for unit in units_before_update}

    # test ordering
    new_unit_list = []
    for unit in units_before_update:
        add_unit = (not unit.isobsolete()
                    and unit.source not in updates
                    and unit.revision > store_revision)
        if add_unit:
            new_unit_list.append(unit.source)
    for source, target_ in units_in_file:
        if source in old_units:
            old_unit = old_units[source]
            should_add = (not old_unit.isobsolete()
                          or old_unit.revision <= store_revision)
            if should_add:
                new_unit_list.append(source)
        else:
            new_unit_list.append(source)
    assert new_unit_list == [x.source for x in store.units]


def _test_store_update_units_now(store, units_in_file, store_revision,
                                 units_before_update):
    # test that all the current units should be there
    updates = {unit[0]: unit[1] for unit in units_in_file}
    old_units = {unit.source: unit for unit in units_before_update}
    for unit in store.units:
        assert (
            unit.source in updates
            or (old_units[unit.source].revision > store_revision
                and not old_units[unit.source].isobsolete()))


@pytest.mark.django_db
def test_store_update(param_update_store_test, member2):
    store = param_update_store_test['store']
    units_in_file = param_update_store_test['units_in_file']
    store_revision = param_update_store_test['store_revision']
    units_before_update = param_update_store_test['units_before_update']

    _test_store_update_indexes(store)

    _test_store_update_units_before(store, units_in_file, store_revision,
                                    units_before_update, member2)

    _test_store_update_units_now(store, units_in_file, store_revision,
                                 units_before_update)

    _test_store_update_ordering(store, units_in_file, store_revision,
                                units_before_update)


@pytest.mark.django_db
def test_store_file_diff(store_diff_tests):
    diff = store_diff_tests['diff']
    store = store_diff_tests['store']
    units_in_file = store_diff_tests['units_in_file']
    store_revision = store_diff_tests['store_revision']

    assert diff.target_store == store
    assert diff.source_revision == store_revision
    assert (
        units_in_file
        == [(x.source, x.target) for x in diff.source_store.units[1:]]
        == [(v['source'], v['target']) for v in diff.source.units.values()])
    assert diff.target.active_uids == [x.source for x in store.units]
    assert diff.target_revision == store.get_max_unit_revision()
    assert (
        diff.target.units
        == {unit["source_f"]: unit
            for unit
            in store.unit_set.values("source_f", "index", "target_f",
                                     "state", "unitid", "id", "revision",
                                     "developer_comment", "translator_comment",
                                     "locations", "context")})
    diff_diff = diff.diff()
    if diff_diff is not None:
        assert (
            sorted(diff_diff.keys())
            == ["add", "index", "obsolete", "update"])

    # obsoleted units have no index - so just check they are all they match
    obsoleted = (store.unit_set.filter(state=OBSOLETE)
                               .filter(revision__gt=store_revision)
                               .values_list("source_f", flat=True))
    assert len(diff.obsoleted_target_units) == obsoleted.count()
    assert all(x in diff.obsoleted_target_units for x in obsoleted)

    assert (
        diff.updated_target_units
        == list(store.units.filter(revision__gt=store_revision)
                           .values_list("source_f", flat=True)))


@pytest.mark.django_db
def test_store_repr():
    store = Store.objects.first()
    assert str(store) == str(store.syncer.convert(store.syncer.file_class))
    assert repr(store) == u"<Store: %s>" % store.pootle_path


@pytest.mark.django_db
def test_store_po_deserializer(test_fs, store_po):

    with test_fs.open("data/po/complex.po") as test_file:
        test_string = test_file.read()
        ttk_po = getclass(test_file)(test_string)

    store_po.update(store_po.deserialize(test_string))
    assert len(ttk_po.units) - 1 == store_po.units.count()


@pytest.mark.django_db
def test_store_po_serializer(test_fs, store_po):

    with test_fs.open("data/po/complex.po") as test_file:
        test_string = test_file.read()
        ttk_po = getclass(test_file)(test_string)

    store_po.update(store_po.deserialize(test_string))
    store_io = io.BytesIO(store_po.serialize())
    store_ttk = getclass(store_io)(store_io.read())
    assert len(store_ttk.units) == len(ttk_po.units)


@pytest.mark.django_db
def test_store_create_name_with_slashes_or_backslashes(tp0):
    """Test Stores are not created with (back)slashes on their name."""

    with pytest.raises(ValidationError):
        Store.objects.create(name="slashed/name.po", parent=tp0.directory,
                             translation_project=tp0)

    with pytest.raises(ValidationError):
        Store.objects.create(name="backslashed\\name.po", parent=tp0.directory,
                             translation_project=tp0)


@pytest.mark.django_db
def test_store_get_file_class():
    store = Store.objects.filter(
        translation_project__project__code="project0",
        translation_project__language__code="language0").first()

    # this matches because po is recognised by ttk
    assert store.syncer.file_class == getclass(store)


@pytest.mark.django_db
def test_store_diff(diffable_stores):
    target_store, source_store = diffable_stores
    differ = StoreDiff(
        target_store,
        source_store,
        target_store.get_max_unit_revision() + 1)
    # no changes
    assert not differ.diff()
    assert differ.target_store == target_store
    assert differ.source_store == source_store


@pytest.mark.django_db
def test_store_diff_delete_target_unit(diffable_stores):
    target_store, source_store = diffable_stores

    # delete a unit in the target store
    remove_unit = target_store.units.first()
    remove_unit.delete()

    # the unit will always be re-added (as its not obsolete)
    # with source_revision to the max
    differ = StoreDiff(
        target_store,
        source_store,
        target_store.get_max_unit_revision())
    result = differ.diff()
    assert result["add"][0][0].source_f == remove_unit.source_f
    assert len(result["add"]) == 1
    assert len(result["index"]) == 0
    assert len(result["obsolete"]) == 0
    assert result['update'] == (set(), {})

    # and source_revision to 0
    differ = StoreDiff(
        target_store,
        source_store,
        0)
    result = differ.diff()
    assert result["add"][0][0].source_f == remove_unit.source_f
    assert len(result["add"]) == 1
    assert len(result["index"]) == 0
    assert len(result["obsolete"]) == 0
    assert result['update'] == (set(), {})


@pytest.mark.django_db
def test_store_diff_delete_source_unit(diffable_stores):
    target_store, source_store = diffable_stores

    # delete a unit in the source store
    remove_unit = source_store.units.first()
    remove_unit.delete()

    # set the source_revision to max and the unit will be obsoleted
    differ = StoreDiff(
        target_store,
        source_store,
        target_store.get_max_unit_revision())
    result = differ.diff()
    to_remove = target_store.units.get(unitid=remove_unit.unitid)
    assert result["obsolete"] == [to_remove.pk]
    assert len(result["obsolete"]) == 1
    assert len(result["add"]) == 0
    assert len(result["index"]) == 0

    # set the source_revision to less that than the target_stores' max_revision
    # and the unit will be ignored, as its assumed to have been previously
    # deleted
    differ = StoreDiff(
        target_store,
        source_store,
        target_store.get_max_unit_revision() - 1)
    assert not differ.diff()


@pytest.mark.django_db
def test_store_diff_delete_obsoleted_target_unit(diffable_stores):
    target_store, source_store = diffable_stores
    # delete a unit in the source store
    remove_unit = source_store.units.first()
    remove_unit.delete()
    # and obsolete the same unit in the target
    obsolete_unit = target_store.units.get(unitid=remove_unit.unitid)
    obsolete_unit.makeobsolete()
    obsolete_unit.save()
    # as the unit is already obsolete - nothing
    differ = StoreDiff(
        target_store,
        source_store,
        target_store.get_max_unit_revision() + 1)
    assert not differ.diff()


@pytest.mark.django_db
def test_store_diff_obsoleted_target_unit(diffable_stores):
    target_store, source_store = diffable_stores
    # obsolete a unit in target
    obsolete_unit = target_store.units.first()
    obsolete_unit.makeobsolete()
    obsolete_unit.save()
    # as the revision is higher it gets unobsoleted
    differ = StoreDiff(
        target_store,
        source_store,
        target_store.get_max_unit_revision() + 1)
    result = differ.diff()
    assert result["update"][0] == set([obsolete_unit.pk])
    assert len(result["update"][1]) == 1
    assert result["update"][1][obsolete_unit.unitid]["dbid"] == obsolete_unit.pk

    # if the revision is less - no change
    differ = StoreDiff(
        target_store,
        source_store,
        target_store.get_max_unit_revision() - 1)
    assert not differ.diff()


@pytest.mark.django_db
def test_store_diff_update_target_unit(diffable_stores):
    target_store, source_store = diffable_stores
    # update a unit in target
    update_unit = target_store.units.first()
    update_unit.target_f = "Some other string"
    update_unit.save()

    # the unit is always marked for update
    differ = StoreDiff(
        target_store,
        source_store,
        target_store.get_max_unit_revision() + 1)
    result = differ.diff()
    assert result["update"][0] == set([update_unit.pk])
    assert result["update"][1] == {}
    assert len(result["add"]) == 0
    assert len(result["index"]) == 0

    differ = StoreDiff(
        target_store,
        source_store,
        0)
    result = differ.diff()
    assert result["update"][0] == set([update_unit.pk])
    assert result["update"][1] == {}
    assert len(result["add"]) == 0
    assert len(result["index"]) == 0


@pytest.mark.django_db
def test_store_diff_update_source_unit(diffable_stores):
    target_store, source_store = diffable_stores
    # update a unit in source
    update_unit = source_store.units.first()
    update_unit.target_f = "Some other string"
    update_unit.save()

    target_unit = target_store.units.get(
        unitid=update_unit.unitid)

    # the unit is always marked for update
    differ = StoreDiff(
        target_store,
        source_store,
        target_store.get_max_unit_revision() + 1)
    result = differ.diff()
    assert result["update"][0] == set([target_unit.pk])
    assert result["update"][1] == {}
    assert len(result["add"]) == 0
    assert len(result["index"]) == 0
    differ = StoreDiff(
        target_store,
        source_store,
        0)
    result = differ.diff()
    assert result["update"][0] == set([target_unit.pk])
    assert result["update"][1] == {}
    assert len(result["add"]) == 0
    assert len(result["index"]) == 0


@pytest.mark.django_db
def test_store_diff_delete_obsoleted_source_unit(diffable_stores):
    target_store, source_store = diffable_stores
    # delete a unit in the target store
    remove_unit = target_store.units.first()
    remove_unit.delete()
    # and obsolete the same unit in the target
    obsolete_unit = source_store.units.get(unitid=remove_unit.unitid)
    obsolete_unit.makeobsolete()
    obsolete_unit.save()
    # as the unit is already obsolete - nothing
    differ = StoreDiff(
        target_store,
        source_store,
        target_store.get_max_unit_revision() + 1)
    assert not differ.diff()


@pytest.mark.django_db
def test_store_syncer(tp0):
    store = tp0.stores.live().first()
    store_tp = store.translation_project
    assert isinstance(store.syncer, PoStoreSyncer)
    assert store.syncer.file_class == getclass(store)
    assert store.syncer.translation_project == store_tp
    assert store.syncer.language == store_tp.language
    assert store.syncer.project == store_tp.project
    assert store.syncer.source_language == store_tp.project.source_language


@pytest.mark.django_db
def test_store_syncer_obsolete_unit(tp0):
    store = tp0.stores.live().first()
    unit = store.units.filter(state=TRANSLATED).first()
    unit_syncer = store.syncer.unit_sync_class(unit)
    newunit = unit_syncer.create_unit(store.syncer.file_class.UnitClass)

    # unit is untranslated, its always just deleted
    obsolete, deleted = store.syncer.obsolete_unit(newunit, True)
    assert not obsolete
    assert deleted
    obsolete, deleted = store.syncer.obsolete_unit(newunit, False)
    assert not obsolete
    assert deleted

    # set unit to translated
    newunit.target = unit.target

    # if conservative, nothings changed
    obsolete, deleted = store.syncer.obsolete_unit(newunit, True)
    assert not obsolete
    assert not deleted

    # not conservative and the unit is deleted
    obsolete, deleted = store.syncer.obsolete_unit(newunit, False)
    assert obsolete
    assert not deleted


@pytest.mark.django_db
def test_store_syncer_sync_store(tp0, dummy_store_syncer):
    store = tp0.stores.live().first()
    DummyStoreSyncer, expected = dummy_store_syncer
    dummy_syncer = DummyStoreSyncer(store, expected=expected)
    result = dummy_syncer.sync_store(
        expected["last_revision"],
        expected["update_structure"],
        expected["conservative"])
    assert result[0] is True
    assert result[1]["updated"] == expected["changes"]
    # conservative makes no diff here
    expected["conservative"] = False
    dummy_syncer = DummyStoreSyncer(store, expected=expected)
    result = dummy_syncer.sync_store(
        expected["last_revision"],
        expected["update_structure"],
        expected["conservative"])
    assert result[0] is True
    assert result[1]["updated"] == expected["changes"]


@pytest.mark.django_db
def test_store_syncer_sync_store_no_changes(tp0, dummy_store_syncer):
    store = tp0.stores.live().first()
    DummyStoreSyncer, expected = dummy_store_syncer
    dummy_syncer = DummyStoreSyncer(store, expected=expected)

    # no changes
    expected["changes"] = []
    expected["conservative"] = True
    dummy_syncer = DummyStoreSyncer(store, expected=expected)
    result = dummy_syncer.sync_store(
        expected["last_revision"],
        expected["update_structure"],
        expected["conservative"])
    assert result[0] is False
    assert not result[1].get("updated")

    # conservative makes no diff here
    expected["conservative"] = False
    dummy_syncer = DummyStoreSyncer(store, expected=expected)
    result = dummy_syncer.sync_store(
        expected["last_revision"],
        expected["update_structure"],
        expected["conservative"])
    assert result[0] is False
    assert not result[1].get("updated")


@pytest.mark.django_db
def test_store_syncer_sync_store_structure(tp0, dummy_store_syncer):
    store = tp0.stores.live().first()
    DummyStoreSyncer, expected = dummy_store_syncer

    expected["update_structure"] = True
    expected["changes"] = []
    dummy_syncer = DummyStoreSyncer(store, expected=expected)
    result = dummy_syncer.sync_store(
        expected["last_revision"],
        expected["update_structure"],
        expected["conservative"])
    assert result[0] is True
    assert result[1]["updated"] == []
    assert result[1]["obsolete"] == 8
    assert result[1]["deleted"] == 9
    assert result[1]["added"] == 10

    expected["obsolete_units"] = []
    expected["new_units"] = []
    expected["changes"] = []
    dummy_syncer = DummyStoreSyncer(store, expected=expected)
    result = dummy_syncer.sync_store(
        expected["last_revision"],
        expected["update_structure"],
        expected["conservative"])
    assert result[0] is False


@pytest.mark.django_db
def test_store_syncer_sync_update_structure(dummy_store_structure_syncer, tp0):
    store = tp0.stores.live().first()
    DummyStoreSyncer, DummyUnit = dummy_store_structure_syncer
    expected = dict(
        unit_class="FOO",
        conservative=True,
        obsolete_delete=(True, True),
        obsolete_units=["a", "b", "c"])
    expected["new_units"] = [
        DummyUnit(unit, expected=expected)
        for unit in ["5", "6", "7"]]
    syncer = DummyStoreSyncer(store, expected=expected)
    result = syncer.update_structure(
        expected["obsolete_units"],
        expected["new_units"],
        expected["conservative"])
    obsolete_units = (
        len(expected["obsolete_units"])
        if expected["obsolete_delete"][0]
        else 0)
    deleted_units = (
        len(expected["obsolete_units"])
        if expected["obsolete_delete"][1]
        else 0)
    new_units = len(expected["new_units"])
    assert result == (obsolete_units, deleted_units, new_units)


def _test_get_new(results, syncer, old_ids, new_ids):
    assert list(results) == list(
        syncer.store.findid_bulk(
            [syncer.dbid_index.get(uid)
             for uid
             in new_ids - old_ids]))


def _test_get_obsolete(results, syncer, old_ids, new_ids):
    assert list(results) == list(
        syncer.disk_store.findid(uid)
        for uid
        in old_ids - new_ids
        if (syncer.disk_store.findid(uid)
            and not syncer.disk_store.findid(uid).isobsolete()))


@pytest.mark.django_db
def test_store_syncer_obsolete_units(dummy_store_syncer_units, tp0):
    store = tp0.stores.live().first()
    expected = dict(
        old_ids=set(),
        new_ids=set(),
        disk_ids={})
    syncer = dummy_store_syncer_units(store, expected=expected)
    results = syncer.get_units_to_obsolete(
        expected["old_ids"], expected["new_ids"])
    _test_get_obsolete(
        results, syncer, expected["old_ids"], expected["new_ids"])
    expected = dict(
        old_ids=set(["2", "3", "4"]),
        new_ids=set(["3", "4", "5"]),
        disk_ids={"3": "foo", "4": "bar", "5": "baz"})
    results = syncer.get_units_to_obsolete(
        expected["old_ids"], expected["new_ids"])
    _test_get_obsolete(
        results, syncer, expected["old_ids"], expected["new_ids"])


@pytest.mark.django_db
def test_store_syncer_new_units(dummy_store_syncer_units, tp0):
    store = tp0.stores.live().first()
    expected = dict(
        old_ids=set(),
        new_ids=set(),
        disk_ids={},
        db_ids={})
    syncer = dummy_store_syncer_units(store, expected=expected)
    results = syncer.get_new_units(
        expected["old_ids"], expected["new_ids"])
    _test_get_new(
        results, syncer, expected["old_ids"], expected["new_ids"])
    expected = dict(
        old_ids=set(["2", "3", "4"]),
        new_ids=set(["3", "4", "5"]),
        db_ids={"3": "foo", "4": "bar", "5": "baz"})
    syncer = dummy_store_syncer_units(store, expected=expected)
    results = syncer.get_new_units(
        expected["old_ids"], expected["new_ids"])
    _test_get_new(
        results, syncer, expected["old_ids"], expected["new_ids"])


@pytest.mark.django_db
def test_store_path(store0):
    assert store0.path == to_tp_relative_path(store0.pootle_path)
