# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import pytest


def pytest_generate_tests(metafunc):
    from pootle_project.models import PROJECT_CHECKERS

    if "checkers" in metafunc.fixturenames:
        metafunc.parametrize("checkers", PROJECT_CHECKERS.keys())


def _require_tp(language, project):
    """Helper to get/create a new translation project."""
    from pootle_translationproject.models import create_translation_project

    return create_translation_project(language, project)


@pytest.fixture
def afrikaans_tutorial(afrikaans, tutorial):
    """Require Afrikaans Tutorial."""
    return _require_tp(afrikaans, tutorial)


@pytest.fixture
def en_tutorial_obsolete(english_tutorial):
    """Require Arabic Tutorial in obsolete state."""
    english_tutorial.directory.makeobsolete()
    return english_tutorial


@pytest.fixture
def english_tutorial(english, tutorial):
    """Require English Tutorial."""
    return _require_tp(english, tutorial)


@pytest.fixture
def italian_tutorial(italian, tutorial):
    """Require Italian Tutorial."""
    return _require_tp(italian, tutorial)


@pytest.fixture
def tp_checker_tests(request, english, checkers):
    from tests.factories import ProjectDBFactory

    checker_name = checkers
    project = ProjectDBFactory(checkstyle=checker_name, source_language=english)
    return (checker_name, project)


@pytest.fixture
def tp0(language0, project0):
    """Require English Project0."""
    from pootle_translationproject.models import TranslationProject

    return TranslationProject.objects.get(language=language0, project=project0)
