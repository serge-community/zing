# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import functools
import os
import shutil
import time
from pkgutil import iter_modules

import pytest

from . import fixtures
from .env import PootleTestEnv
from .fixtures import models as fixtures_models
from .fixtures.core import utils as fixtures_core_utils


def _load_fixtures(*modules):
    for mod in modules:
        path = mod.__path__
        prefix = '%s.' % mod.__name__

        for loader_, name, is_pkg in iter_modules(path, prefix):
            if not is_pkg:
                yield name


def pytest_addoption(parser):
    parser.addoption(
        "--debug-tests",
        action="store",
        default="",
        help="Debug tests to a given file")


@pytest.fixture(autouse=True)
def test_timing(request, settings, log_timings):
    from django.db import reset_queries

    if not request.config.getoption("--debug-tests"):
        return
    settings.DEBUG = True
    reset_queries()
    start = time.time()
    request.addfinalizer(
        functools.partial(
            log_timings,
            request.node.name,
            start))


@pytest.fixture
def po_test_dir(request, tmpdir):
    po_dir = str(tmpdir.mkdir("po"))

    def rm_po_dir():
        if os.path.exists(po_dir):
            shutil.rmtree(po_dir)

    request.addfinalizer(rm_po_dir)
    return po_dir


@pytest.fixture
def po_directory(request, po_test_dir, settings):
    """Sets up a tmp directory for PO files."""
    from pootle_store.models import fs

    translation_directory = settings.ZING_TRANSLATION_DIRECTORY

    # Adjust locations
    settings.ZING_TRANSLATION_DIRECTORY = po_test_dir
    fs.location = po_test_dir

    def _cleanup():
        settings.ZING_TRANSLATION_DIRECTORY = translation_directory

    request.addfinalizer(_cleanup)


@pytest.fixture(scope='session')
def tests_use_db(request):
    return bool(
        [item for item in request.node.items
         if item.get_marker('django_db')])


@pytest.fixture(scope='session')
def tests_use_migration(request, tests_use_db):
    return bool(
        tests_use_db
        and [item for item in request.node.items
             if item.get_marker('django_migration')])


@pytest.fixture(autouse=True, scope='session')
def setup_db_if_needed(request, tests_use_db):
    """Sets up the site DB only if tests requested to use the DB (autouse)."""
    if tests_use_db and not request.config.getvalue('reuse_db'):
        return request.getfuncargvalue('post_db_setup')


@pytest.fixture(scope='session')
def data_dir():
    return lambda path: os.path.join(
        os.path.dirname(__file__), 'data', path
    )


@pytest.fixture(scope='session')
def post_db_setup(translations_directory, django_db_setup, django_db_blocker,
                  tests_use_db, request, data_dir):
    """Sets up the site DB for the test session."""
    if not tests_use_db:
        return

    with django_db_blocker.unblock():
        PootleTestEnv(data_file=data_dir('data_dump.json')).setup()


@pytest.fixture(scope='session')
def django_db_use_migrations(tests_use_migration):
    return tests_use_migration


@pytest.fixture
def test_name(request):
    """Provides current test function's name as a string."""
    return request.node.originalname or request.node.name


pytest_plugins = tuple(
    _load_fixtures(
        fixtures,
        fixtures_core_utils,
        fixtures_models,
    )
)
