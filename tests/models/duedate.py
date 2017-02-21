# -*- coding: utf-8 -*-
#
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import pytest

from django.core.exceptions import ValidationError

from pytest_pootle.factories import DueDateFactory, UserFactory

from pootle.core.utils.timezone import aware_datetime
from pootle.models import DueDate
from pootle_translationproject.models import TranslationProject


@pytest.mark.django_db
@pytest.mark.parametrize('pootle_path', [
    '/',
    '/projects/',
    '/ru/',
])
def test_duedate_create_invalid_paths(pootle_path):
    """Tests certain path restrictions when creating due dates."""
    with pytest.raises(ValidationError) as excinfo:
        DueDateFactory.create(pootle_path=pootle_path)

    message_dict = excinfo.value.message_dict
    assert 'pootle_path' in message_dict
    assert 'Cannot set due date for this path.' in message_dict['pootle_path']


@pytest.mark.django_db
@pytest.mark.parametrize('pootle_path', [
    '/ru/foo/',
    '/ru/foo/bar/',
    '/ru/foo/bar/baz.po',
    '/projects/foo/',
    '/projects/foo/bar/',
    '/projects/foo/bar/baz.po',
])
def test_duedate_create(pootle_path):
    """Tests due dates creation for valid paths."""
    due_date = DueDateFactory.create(
        pootle_path=pootle_path,
    )
    assert due_date.id is not None


@pytest.mark.django_db
def test_duedate_create_project_propagates():
    """Tests due date creation at the project level propagates to
    existing TPs.
    """
    project_code = 'project0'
    pootle_path = '/projects/%s/' % project_code
    DueDateFactory.create(
        pootle_path=pootle_path,
    )

    tp_due_dates = DueDate.objects.for_project(project_code).exclude(
        pootle_path__startswith=pootle_path,
    )
    tps = TranslationProject.objects.filter(project__code=project_code)
    assert tp_due_dates.count() == tps.count() != 0


@pytest.mark.django_db
def test_duedate_update_project_propagates():
    """Tests due date updates at the project level propagates to
    existing TP due dates.
    """
    project_code = 'project0'
    pootle_path = '/projects/%s/' % project_code
    due_date = DueDateFactory.create(
        pootle_path=pootle_path,
    )

    # Update due date with different values
    other_user = UserFactory.create()
    other_due_on = aware_datetime(2017, 1, 1, 1, 2, 3)
    due_date.due_on = other_due_on
    due_date.modified_by = other_user
    due_date.save()

    tp_due_dates = DueDate.objects.for_project(project_code).exclude(
        pootle_path__startswith=pootle_path,
    )
    for tp_due_date in tp_due_dates:
        assert tp_due_date.due_on == other_due_on
        assert tp_due_date.modified_by == other_user


@pytest.mark.django_db
def test_duedate_delete_project_propagates():
    """Tests due date deletion at the project level propagates to
    existing TP due dates.
    """
    project_code = 'project0'
    pootle_path = '/projects/%s/' % project_code
    due_date = DueDateFactory.create(
        pootle_path=pootle_path,
    )

    tp_due_dates = DueDate.objects.for_project(project_code).exclude(
        pootle_path__startswith=pootle_path,
    )
    tps = TranslationProject.objects.filter(project__code=project_code)
    assert tp_due_dates.count() == tps.count() != 0

    due_date.delete()

    tp_due_dates = DueDate.objects.for_project(project_code).exclude(
        pootle_path__startswith=pootle_path,
    )

    assert tp_due_dates.count() == 0
