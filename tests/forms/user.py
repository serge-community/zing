# -*- coding: utf-8 -*-
#
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import pytest

from pootle_app.forms import UserForm


@pytest.mark.parametrize('linkedin_value', [
    None,
    '',
    ' ',
])
@pytest.mark.django_db
def test_user_clean_linkedin_no_value(linkedin_value):
    """Tests validation of the `linkedin` field with empty/null values."""
    form_data = {
        'username': 'foo',
        'password': 'bar',
        'email': 'foo@bar.baz',
        'linkedin': linkedin_value,
    }
    form = UserForm(form_data)
    assert form.is_valid()
    assert form.cleaned_data['linkedin'] is None


@pytest.mark.parametrize('linkedin_value', [
    'foo bar',
    'example.com',
    'linkedin.com',
    'http://example.com',
    'http://linkedin.com',
    'https://jp.linkedin.com',
    'https://linkedin.com/',
    'https://linkedin.com/in/',
])
@pytest.mark.django_db
def test_user_clean_linkedin_invalid_url(linkedin_value):
    """Tests validation of the `linkedin` field with invalid URLs."""
    form_data = {
        'username': 'foo',
        'password': 'bar',
        'email': 'foo@bar.baz',
        'linkedin': linkedin_value,
    }
    form = UserForm(form_data)
    assert not form.is_valid()
    assert form.has_error('linkedin')


@pytest.mark.parametrize('linkedin_value', [
    'https://linkedin.com/in/foo',
    'https://jp.linkedin.com/in/foo',
    'https://linkedin.com/in/foo-bar-baz',
])
@pytest.mark.django_db
def test_user_clean_linkedin_valid_url(linkedin_value):
    """Tests validation of the `linkedin` field with valid URLs."""
    form_data = {
        'username': 'foo',
        'password': 'bar',
        'email': 'foo@bar.baz',
        'linkedin': linkedin_value,
    }
    form = UserForm(form_data)
    assert form.is_valid()
    assert form.cleaned_data['linkedin'] == linkedin_value
