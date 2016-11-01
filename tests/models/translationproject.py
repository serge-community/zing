# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
#
# This file is a part of the Pootle project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import os

import pytest

from translate.filters import checks

from django.db import IntegrityError

from pytest_pootle.factories import (
    LanguageDBFactory, ProjectDBFactory, TranslationProjectFactory)

from pootle_language.models import Language
from pootle_project.models import Project
from pootle_store.models import Store
from pootle_translationproject.models import TranslationProject


@pytest.mark.django_db
def test_tp_create_fail(po_directory, tutorial, english):

    # Trying to create a TP with no Language raises a RelatedObjectDoesNotExist
    # which can be caught with Language.DoesNotExist
    with pytest.raises(Language.DoesNotExist):
        TranslationProject.objects.create()

    # TP needs a project set too...
    with pytest.raises(Project.DoesNotExist):
        TranslationProject.objects.create(language=english)

    # There is already an english tutorial was automagically set up
    with pytest.raises(IntegrityError):
        TranslationProject.objects.create(project=tutorial, language=english)


@pytest.mark.django_db
def test_tp_create_with_files(project0_directory, project0, store0, settings):
    # lets add some files by hand

    trans_dir = settings.POOTLE_TRANSLATION_DIRECTORY
    language = LanguageDBFactory()
    tp_dir = os.path.join(trans_dir, "%s/project0" % language.code)
    os.makedirs(tp_dir)

    with open(os.path.join(tp_dir, "store0.po"), "w") as f:
        f.write(store0.serialize())

    TranslationProject.objects.create(project=project0, language=language)


@pytest.mark.django_db
def test_tp_checker(po_directory, tp_checker_tests):
    language = Language.objects.get(code="language0")
    checker_name_, project = tp_checker_tests
    tp = TranslationProject.objects.create(project=project, language=language)

    checkerclasses = [
        checks.projectcheckers.get(tp.project.checkstyle,
                                   checks.StandardChecker)
    ]
    assert [x.__class__ for x in tp.checker.checkers] == checkerclasses


@pytest.mark.django_db
def test_tp_create_with_none_treestyle(po_directory, english, templates, settings):
    project = ProjectDBFactory(
        source_language=english,
        treestyle="none")
    language = LanguageDBFactory()
    TranslationProjectFactory(
        language=templates, project=project)

    tp = TranslationProject.objects.create(
        project=project, language=language)

    assert not tp.abs_real_path
    assert not os.path.exists(
        os.path.join(
            settings.POOTLE_TRANSLATION_DIRECTORY,
            project.code))

    tp.save()
    assert not tp.abs_real_path
    assert not os.path.exists(
        os.path.join(
            settings.POOTLE_TRANSLATION_DIRECTORY,
            project.code))


def _test_tp_match(source_tp, target_tp):
    source_stores = []
    for store in source_tp.stores.live():
        source_stores.append(store.pootle_path)
        update_path = (
            "/%s/%s"
            % (target_tp.language.code,
               store.pootle_path[(len(source_tp.language.code) + 2):]))
        updated = Store.objects.get(pootle_path=update_path)
        assert store.state == updated.state
        updated_units = updated.units
        for i, unit in enumerate(store.units):
            updated_unit = updated_units[i]
            assert unit.source == updated_unit.source
            assert unit.target == updated_unit.target
            assert unit.state == updated_unit.state
    for store in target_tp.stores.live():
        source_path = (
            "/%s/%s"
            % (source_tp.language.code,
               store.pootle_path[(len(target_tp.language.code) + 2):]))
        assert source_path in source_stores
