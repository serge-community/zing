# -*- coding: utf-8 -*-
#
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import pytest

from django.utils import timezone

from pootle.core.utils import dateformat
from pootle.forms import DueDateForm


@pytest.mark.django_db
@pytest.mark.parametrize('pootle_path', [
    '/ru/',
    '/ru/foo/',
    '/ru/foo/bar/',
    '/ru/foo/bar/baz.po',
    '/projects/foo/',
    '/projects/foo/bar/',
    '/projects/foo/bar/baz.po',
])
def test_duedate_create(pootle_path, request_users):
    """Tests form validation for a set of paths."""
    user = request_users['user']

    form_data = {
        'due_on': dateformat.format(timezone.now(), 'U'),
        'modified_by': user.id,
        'pootle_path': pootle_path,
    }
    form = DueDateForm(form_data)
    print form.errors
    assert form.is_valid()
    due_date = form.save()
    assert due_date.id is not None
