# -*- coding: utf-8 -*-
#
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from datetime import timedelta

import pytest

from pytest_pootle.factories import DueDateFactory
from pytest_pootle.utils import as_dir

from pootle.core.utils.timezone import aware_datetime
from pootle.models.task import CriticalTask, TaskResultSet, TranslationTask


def test_translation_task_repr():
    """Tests `TranslationTask`'s representation."""
    due_on = now = aware_datetime(2017, 02, 28, 9, 00)
    due_date = DueDateFactory.build(due_on=due_on)
    task = TranslationTask(
        due_date=due_date,
        now=now,
        words_left=1,
    )
    assert (
        task.__repr__() == '<TranslationTask: /foo/ (2017-02-28 09:00:00+01:00)>'
    )


@pytest.mark.parametrize('words_left, days_left, expected_factor', [
    (1500, 10, 0.15),
    (20, 10, 0.002),
    (5000, 10, 0.5),
    (5000, 5, 1),
    (1000, 1, 1),
    (100, 1, 0.1),
    (2000, 1, 1),
    (100, -10, 1),
    (1, 0, 1),
])
def test_translation_task_importance_factor(words_left, days_left,
                                            expected_factor):
    """Tests `TranslationTask`'s importance factor."""
    now = aware_datetime(2017, 02, 28, 9, 00)
    due_on = now + timedelta(days=days_left)
    due_date = DueDateFactory.build(due_on=due_on)
    task = TranslationTask(
        due_date=due_date,
        now=now,
        words_left=words_left,
    )
    assert task.importance_factor == expected_factor


@pytest.mark.parametrize('words_left, days_left, expected_factor', [
    (1, 5, 0.2),
    (1, 1, 1),
    (20, 1, 1),
])
def test_critical_task_importance_factor(words_left, days_left,
                                         expected_factor):
    """Tests `CriticalTask`'s importance factor."""
    now = aware_datetime(2017, 02, 28, 9, 00)
    due_on = now + timedelta(days=days_left)
    due_date = DueDateFactory.build(due_on=due_on)
    task = CriticalTask(
        due_date=due_date,
        now=now,
        words_left=words_left,
    )
    assert task.importance_factor == expected_factor


@pytest.mark.django_db
def test_taskresultset_get_single():
    """Tests retrieving a single task resultset item by index."""
    due_on = now = aware_datetime(2017, 02, 28, 9, 00)
    due_date = DueDateFactory.build(due_on=due_on)
    task = TranslationTask(
        due_date=due_date,
        now=now,
        words_left=1,
    )
    task_resultset = TaskResultSet([task])
    assert task_resultset[0] == task.data


@pytest.mark.parametrize('index', [None, 1.0, '1'])
def test_taskresultset_get_raises(index):
    """Tests retrieving from a task resultset by using an invalid index/slice."""
    due_on = now = aware_datetime(2017, 02, 28, 9, 00)
    due_date = DueDateFactory.build(due_on=due_on)
    task = TranslationTask(
        due_date=due_date,
        now=now,
        words_left=1,
    )
    task_resultset = TaskResultSet([task])
    with pytest.raises(TypeError):
        task_resultset[index]


class LightTask(object):
    def __init__(self, importance_factor, days_left, path, *args, **kwargs):
        self.importance_factor = importance_factor
        self.days_left = days_left
        self.due_date = DueDateFactory.build(pootle_path=path)

    @property
    def data(self):
        return {
            'path': self.due_date.pootle_path,
            'days_left': self.days_left,
            'importance_factor': self.importance_factor,
        }


@pytest.mark.parametrize('sort_type, fake_task_args', [
    ('importance', [
        # importance, days left, path
        (1, 5, '/foo/bar/baz/'),
        (0.3, 7, '/foo/bar/'),
        (0.2, 6, '/foo/'),
        (0.0002, 4, '/bar/baz/'),
        (0.0002, 9, '/bar/'),
        (1, 8, '/baz/'),
        (1, 5, '/blah/'),
    ]),
    ('days_left', [
        (1, 8, '/foo/bar/baz/'),
        (1, -6, '/foo/'),
        (1, 7, '/foo/bar/'),
        (1, -4, '/bar/baz/'),
        (1, 9, '/bar/'),
        (1, 5, '/baz/'),
        (1, 3, '/blah/'),
    ]),
    ('days_left_and_path', [
        (1, 5, '/foo/bar/baz/'),
        (1, 5, '/foo/'),
        (1, 5, '/foo/bar/'),
        (1, 2, '/bar/baz/'),
        (1, 1, '/bar/'),
        (1, 5, '/baz/'),
        (1, 0, '/blah/'),
    ]),
    ('path', [
        (1, 5, '/foo/bar/baz/'),
        (1, 5, '/foo/'),
        (1, 5, '/foo/bar/'),
        (1, 5, '/blah/'),
        (1, 5, '/baz/'),
        (1, 5, '/bar/baz/'),
        (1, 5, '/bar/'),
    ]),
])
def test_taskresultset_importance_order(test_name, snapshot_stack,
                                        sort_type, fake_task_args):
    """Tests ordering of tasks according to their importance."""
    tasks = [LightTask(*task_args) for task_args in fake_task_args]
    with snapshot_stack.push([as_dir(test_name), sort_type]) as snapshot:
        task_resultset = TaskResultSet(tasks).order_by_importance()
        snapshot.assert_matches([task for task in task_resultset])
