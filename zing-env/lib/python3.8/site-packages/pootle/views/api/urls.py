# -*- coding: utf-8 -*-
#
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from django.conf.urls import url

from .duedate import DueDateView
from .task import TaskView


urlpatterns = [
    url(
        r"^duedates/((?P<id>[0-9]+)/)?$",
        DueDateView.as_view(),
        name="zing-xhr-duedates",
    ),
    url(
        r"^tasks/(?P<language_code>[^/]*)/$", TaskView.as_view(), name="zing-xhr-tasks"
    ),
]
