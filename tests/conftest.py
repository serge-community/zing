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

from django import setup
from django.conf import settings

import logging

logging.getLogger("factory").setLevel(logging.WARN)

WORKING_DIR = os.path.abspath(os.path.dirname(__file__))


def pytest_addoption(parser):
    parser.addoption(
        '--generate-snapshots',
        dest='generate_snapshots',
        action='store_true',
        default=False,
        help='Generate snapshots for tests marked with the `snapshot` mark.'
    )


@pytest.fixture
def should_generate_snapshots(pytestconfig):
    """Indicates whether snapshots have been instructed to be generated."""
    return bool(pytestconfig.getoption('generate_snapshots'))


def pytest_collection_modifyitems(items, config):
    """When willing to generate snapshots, only consider tests that
    make actual use of the snapshot stack.
    """
    if not config.getoption('generate_snapshots'):
        return

    selected_items = []
    deselected_items = []

    for item in items:
        if 'snapshot_stack' in item.fixturenames:
            selected_items.append(item)
        else:
            deselected_items.append(item)
    config.hook.pytest_deselected(items=deselected_items)
    items[:] = selected_items


@pytest.fixture
def tests_dir():
    """Helper function to join a path relative to the tests directory."""
    return lambda path: os.path.join(WORKING_DIR, path)


def pytest_configure():
    if not settings.configured:
        from pootle import syspath_override  # Needed for monkey-patching
        syspath_override
        os.environ['DJANGO_SETTINGS_MODULE'] = 'pootle.settings'
        os.environ['POOTLE_SETTINGS'] = os.path.join(WORKING_DIR, 'settings.py')
        # The call to `setup()` was needed before a fix for
        # pytest-dev/pytest-django#146 was available. This happened in version
        # 2.9; unfortunately upgrading to 2.9+ is not possible yet because a fix
        # for pytest-dev/pytest-django#289 is needed too, and this is not part
        # of any releases for the time being.
        setup()


pytest_plugins = 'pytest_pootle.plugin'
