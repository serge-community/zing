# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import pytest

from pootle_app.forms import ProjectForm
from pootle_project.models import PROJECT_CHECKERS, RESERVED_PROJECT_CODES


@pytest.mark.parametrize('reserved_code', RESERVED_PROJECT_CODES)
@pytest.mark.django_db
def test_clean_code_invalid(reserved_code):
    form_data = {
        'code': reserved_code,
        'checkstyle': list(PROJECT_CHECKERS.keys())[0],
        'fullname': 'Foo',
        'source_language': 1,
    }
    form = ProjectForm(form_data)
    assert not form.is_valid()
    assert 'code' in form.errors
    assert len(list(form.errors.keys())) == 1


@pytest.mark.django_db
def test_clean_code_blank_invalid():
    form_data = {
        'code': '  ',
        'checkstyle': list(PROJECT_CHECKERS.keys())[0],
        'fullname': 'Foo',
        'source_language': 1,
    }
    form = ProjectForm(form_data)
    assert not form.is_valid()
    assert 'code' in form.errors
    assert len(list(form.errors.keys())) == 1
