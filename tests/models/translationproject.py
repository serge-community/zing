# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import os

import pytest

from translate.filters import checks

from django.db import IntegrityError

from pytest_pootle.factories import LanguageDBFactory

from pootle_language.models import Language
from pootle_misc.util import import_func
from pootle_project.models import Project
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
    trans_dir = settings.ZING_TRANSLATION_DIRECTORY
    language = LanguageDBFactory()
    tp_dir = os.path.join(trans_dir, "project0/%s" % language.code)
    os.makedirs(tp_dir)

    with open(os.path.join(tp_dir, "store0.po"), "w") as f:
        f.write(store0.serialize())

    TranslationProject.objects.create(project=project0, language=language)


@pytest.mark.django_db
def test_tp_checker(po_directory, tp_checker_tests, settings):
    language = Language.objects.get(code="language0")
    checker_name_, project = tp_checker_tests
    tp = TranslationProject.objects.create(project=project, language=language)

    if settings.POOTLE_QUALITY_CHECKER:
        checkerclasses = [import_func(settings.POOTLE_QUALITY_CHECKER)]
    else:
        checkerclasses = [
            checks.projectcheckers.get(tp.project.checkstyle,
                                       checks.StandardChecker)
        ]
    assert [x.__class__ for x in tp.checker.checkers] == checkerclasses
