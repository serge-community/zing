# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
#
# This file is a part of the Pootle project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import pytest

from pytest_pootle.factories import ProjectDBFactory, TranslationProjectFactory

from pootle.core.delegate import formats
from pootle_format.exceptions import UnrecognizedFiletype
from pootle_format.models import Format
from pootle_store.models import Store


@pytest.mark.django_db
def test_format_util(project0):

    filetype_tool = project0.filetype_tool
    assert list(filetype_tool.filetypes.all()) == list(project0.filetypes.all())

    assert filetype_tool.filetype_extensions == [u"po"]

    xliff = Format.objects.get(name="xliff")
    project0.filetypes.add(xliff)
    assert filetype_tool.filetype_extensions == [u"po", u"xliff"]


@pytest.mark.django_db
def test_format_chooser(project0):
    registry = formats.get()
    po = Format.objects.get(name="po")
    po2 = registry.register("special_po_2", "po")
    po3 = registry.register("special_po_3", "po")
    xliff = Format.objects.get(name="xliff")
    project0.filetypes.add(xliff)
    project0.filetypes.add(po2)
    project0.filetypes.add(po3)
    filetype_tool = project0.filetype_tool
    from pootle.core.debug import debug_sql
    with debug_sql():
        assert filetype_tool.choose_filetype("foo.po") == po
    assert filetype_tool.choose_filetype("foo.xliff") == xliff

    # push po to the back of the queue
    project0.filetypes.remove(po)
    project0.filetypes.add(po)
    assert filetype_tool.choose_filetype("foo.po") == po2
    assert filetype_tool.choose_filetype("foo.xliff") == xliff

    with pytest.raises(UnrecognizedFiletype):
        filetype_tool.choose_filetype("foo.bar")


@pytest.mark.django_db
def test_format_add_project_filetype(project0, po2):
    project = project0
    project.filetype_tool.add_filetype(po2)
    assert po2 in project.filetypes.all()

    # adding a 2nd time does nothing
    project.filetype_tool.add_filetype(po2)
    assert project.filetypes.filter(pk=po2.pk).count() == 1


@pytest.mark.django_db
def test_format_set_store_filetype(project0):
    project = project0
    store = Store.objects.filter(
        translation_project__project=project).first()
    store_name = store.name
    registry = formats.get()
    filetypes = project.filetype_tool

    # register po2
    po2 = registry.register("special_po_2", "po")

    # filetype must be recognized for project
    with pytest.raises(UnrecognizedFiletype):
        filetypes.set_store_filetype(store, po2)

    # add the filetype to the project
    filetypes.add_filetype(po2)

    # set the store's filetype
    filetypes.set_store_filetype(store, po2)

    # the filetype is changed, but the extension is the same
    store = Store.objects.get(pk=store.pk)
    assert store.filetype == po2
    assert store.name == store_name

    # register po3 - different extension
    po3 = registry.register("special_po_3", "po3")
    filetypes.add_filetype(po3)
    filetypes.set_store_filetype(store, po3)

    # the filetype is changed, and the extension
    store = Store.objects.get(pk=store.pk)
    assert store.filetype == po3
    assert store.name.endswith(".po3")
    assert store.pootle_path.endswith(".po3")


@pytest.mark.django_db
def test_format_set_tp_filetype(po_directory, english, language0, po2):
    project = ProjectDBFactory(source_language=english)
    filetypes = project.filetype_tool
    registry = formats.get()
    lang_tp = TranslationProjectFactory(language=language0, project=project)
    store = Store.objects.create(
        name="mystore.po",
        translation_project=lang_tp,
        parent=lang_tp.directory)
    filetypes.add_filetype(po2)
    filetypes.set_tp_filetype(lang_tp, po2)
    store = Store.objects.get(pk=store.pk)
    assert store.filetype == po2
    assert store.name.endswith(".po2")
    po3 = registry.register("special_po_3", "po3")
    filetypes.add_filetype(po3)
    filetypes.set_tp_filetype(lang_tp, po3)
    store = Store.objects.get(pk=store.pk)
    assert store.filetype == po3
    assert store.name.endswith(".po3")


@pytest.mark.django_db
def test_format_set_tp_matching_filetype(tp0, po, po2):
    project = tp0.project
    project.filetype_tool.add_filetype(po2)

    store5 = tp0.stores.get(name="store5.po")
    assert store5.filetype == po
    project.filetype_tool.set_tp_filetype(tp0, po2, matching="store5")

    # doesnt match - because its in a subdir
    store5 = Store.objects.get(pk=store5.pk)
    assert store5.filetype == po

    project.filetype_tool.set_tp_filetype(tp0, po2, matching="*store5")
    store5 = Store.objects.get(pk=store5.pk)
    assert store5.filetype == po2

    project.filetype_tool.set_tp_filetype(tp0, po, matching="*/*5")
    store5 = Store.objects.get(pk=store5.pk)
    assert store5.filetype == po


@pytest.mark.django_db
def test_format_set_project_filetypes(tp0, dummy_project_filetypes, po2):
    project = tp0.project
    tps = project.translationproject_set.all()
    filetype_tool = project.filetype_tool
    result = filetype_tool.result

    with pytest.raises(UnrecognizedFiletype):
        filetype_tool.set_filetypes(po2)

    filetype_tool.add_filetype(po2)
    filetype_tool.set_filetypes(po2)

    for i, tp in enumerate(tps):
        assert result[i] == (tp, po2, None, None)

    # test getting from_filetype
    result.clear()
    filetype_tool.set_filetypes(po2, from_filetype="foo")
    for i, tp in enumerate(tps):
        assert result[i] == (tp, po2, "foo", None)

    # test getting match
    result.clear()
    filetype_tool.set_filetypes(po2, matching="bar")
    for i, tp in enumerate(tps):
        assert result[i] == (tp, po2, None, "bar")

    # test getting both
    result.clear()
    filetype_tool.set_filetypes(po2, from_filetype="foo", matching="bar")
    for i, tp in enumerate(tps):
        assert result[i] == (tp, po2, "foo", "bar")
