# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Pootle project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import pytest

from django.urls import reverse_lazy, reverse

from pootle_language.models import Language
from pootle_project.models import Project


ADMIN_URL = reverse_lazy('pootle-admin')


@pytest.mark.django_db
def test_admin_not_logged_in(client):
    """Checks logged-out users cannot access the admin site."""
    response = client.get(ADMIN_URL)
    assert response.status_code == 403


@pytest.mark.django_db
def test_admin_regular_user(client, default):
    """Checks regular users cannot access the admin site."""
    client.login(username=default.username, password='')
    response = client.get(ADMIN_URL)
    assert response.status_code == 403


@pytest.mark.django_db
def test_admin_access(client):
    """Tests that admin users can access the admin site."""
    client.login(username="admin", password="admin")
    response = client.get(ADMIN_URL)
    assert response.status_code == 200


@pytest.mark.django_db
def test_admin_view_projects(client, request_users, english):
    user = request_users["user"]

    client.force_login(user)

    response = client.get(
        reverse(
            "pootle-admin-projects"))

    if not user.is_superuser:
        assert response.status_code == 403
        return
    languages = Language.objects.all()
    language_choices = [(lang.id, unicode(lang)) for lang in languages]
    expected = {
        'page': 'admin-projects',
        'form_choices': {
            'checkstyle': Project.checker_choices,
            'source_language': language_choices,
            'defaults': {
                'source_language': english.id}}}
    for k, v in expected.items():
        assert response.context_data[k] == v
