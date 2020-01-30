# -*- coding: utf-8 -*-
#
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import pytest

from pootle.forms import AddDueDateForm, EditDueDateForm


@pytest.mark.django_db
@pytest.mark.parametrize(
    "pootle_path",
    [
        "/ru/foo/",
        "/ru/foo/bar/",
        "/ru/foo/bar/baz.po",
        "/projects/foo/",
        "/projects/foo/bar/",
        "/projects/foo/bar/baz.po",
    ],
)
def test_duedate_create_update(pootle_path, request_users):
    """Tests form validation for a set of paths."""
    user = request_users["user"]

    form_data = {
        "due_on": "2016-04-03",
        "modified_by": user.id,
        "pootle_path": pootle_path,
    }
    form = AddDueDateForm(form_data)
    assert form.is_valid()
    due_date = form.save()
    assert due_date.id is not None

    old_due_on = due_date.due_on
    edit_form_data = {
        "due_on": "2016-04-04",
    }
    edit_form = EditDueDateForm(data=edit_form_data, instance=due_date)
    assert edit_form.is_valid()
    updated = edit_form.save()
    assert updated.due_on != old_due_on
