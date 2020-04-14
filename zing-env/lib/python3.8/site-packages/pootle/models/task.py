# -*- coding: utf-8 -*-
#
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from datetime import timedelta


WORDS_PER_DAY = 1000


def days_left(from_datetime, to_datetime):
    seconds_difference = (to_datetime - from_datetime).total_seconds()
    seconds_per_day = timedelta(days=1).total_seconds()
    return seconds_difference / seconds_per_day


class TranslationTask(object):
    type = "translation"
    weight = 1

    def __init__(self, due_date, now, words_left, **kwargs):
        self.due_date = due_date
        self.now = now
        self.words_left = words_left

    def __repr__(self):
        return "<%s: %s (%s)>" % (
            self.__class__.__name__,
            self.due_date.pootle_path,
            self.due_date.due_on,
        )

    @property
    def days_left(self):
        return days_left(self.now, self.due_date.due_on)

    @property
    def importance_factor(self):
        if self.days_left < 1:
            return 1

        factor = (self.words_left * self.weight / self.days_left) / WORDS_PER_DAY
        return 1 if factor > 1 else factor

    @property
    def data(self):
        return {
            "type": self.type,
            "words_left": self.words_left,
            "importance_factor": self.importance_factor,
            "due_date_id": self.due_date.id,
            "path": self.due_date.pootle_path,
            "due_on": self.due_date.due_on,
            "project_name": self.due_date.project_name,
        }


class CriticalTask(TranslationTask):
    type = "critical"
    # For critical tasks, fixing one problematic unit is as important
    # as translating 1000 words
    weight = 1000


class TaskResultSet(object):
    def __init__(self, tasks, *args, **kwargs):
        self.tasks = tasks
        self.total = len(tasks)

    def __getitem__(self, k):
        """Retrieves an item or slice from the set of results."""
        if not isinstance(k, (slice, int)):
            raise TypeError

        if isinstance(k, slice):
            start = int(k.start) if k.start is not None else 0
            stop = int(k.stop) if k.stop is not None else -1
            tasks = self.tasks[start:stop]
            return [item.data for item in tasks]

        return self.tasks[k].data

    def order_by_importance(self):
        self.tasks = sorted(
            self.tasks,
            key=lambda x: (-x.importance_factor, x.days_left, x.due_date.pootle_path),
        )
        return self

    def order_by_deadline(self):
        self.tasks = sorted(
            self.tasks, key=lambda x: (x.days_left, x.due_date.pootle_path),
        )
        return self
