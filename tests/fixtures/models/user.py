# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import copy

import pytest

from .language import language0


TEST_USERS = {
    'nobody': dict(
        fullname='Nobody',
        password=''),
    'system': dict(
        fullname='System',
        password=''),
    'default': dict(
        fullname='Default',
        password=''),
    'admin': dict(
        fullname='Admin',
        password='admin',
        is_superuser=True,
        email="admin@poot.le"),
    'member': dict(
        fullname='Member',
        password='',
        alt_src_lang=language0),
    'member2': dict(
        fullname='Member2',
        password='')}


def _get_user(username):
    user_dict = copy.deepcopy(TEST_USERS[username])
    user_dict.update({
        'user': _require_user(username=username, **user_dict),
    })
    return user_dict


@pytest.fixture(params=['nobody', 'admin', 'member'])
def request_users(request):
    return _get_user(request.param)


@pytest.fixture(params=TEST_USERS.keys())
def site_users(request):
    return _get_user(request.param)


@pytest.fixture(params=['default', 'nobody', 'system'])
def meta_users(request):
    """Require meta users."""
    return _get_user(request.param)


def _require_user(username, fullname, password=None,
                  is_superuser=False, email=None, alt_src_lang=None):
    """Helper to get/create a new user."""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    email = email if email is not None else '%s@example.com' % username
    criteria = {
        'username': username,
        'full_name': fullname,
        'email': email,
        'is_active': True,
        'is_superuser': is_superuser,
    }
    user, created = User.objects.get_or_create(**criteria)

    if created:
        if password is None:
            user.set_unusable_password()
        else:
            user.set_password(password)
        user.save()

    if alt_src_lang is not None:
        user.alt_src_langs.add(alt_src_lang())

    return user


@pytest.fixture
def nobody():
    """Require the default anonymous user."""
    from django.contrib.auth import get_user_model

    return get_user_model().objects.get_nobody_user()


@pytest.fixture
def default():
    """Require the default authenticated user."""
    from django.contrib.auth import get_user_model

    return get_user_model().objects.get_default_user()


@pytest.fixture
def system():
    """Require the system user."""
    from django.contrib.auth import get_user_model

    return get_user_model().objects.get_system_user()


@pytest.fixture
def admin():
    """Require the admin user."""
    from django.contrib.auth import get_user_model

    return get_user_model().objects.get(username="admin")


@pytest.fixture
def member():
    """Require a member user."""
    from django.contrib.auth import get_user_model

    return get_user_model().objects.get(username="member")


@pytest.fixture
def unverified_member():
    """Require a user with an unverified email."""
    return _require_user('unverified_member', 'Unverified member')


@pytest.fixture
def trans_member():
    """Require a member user."""
    return _require_user('trans_member', 'Transactional member')


@pytest.fixture
def member2():
    """Require a member2 user."""
    from django.contrib.auth import get_user_model

    return get_user_model().objects.get(username="member2")


@pytest.fixture
def unverified_member2():
    """Require another user with an unverified email."""
    return _require_user('unverified_member2', 'Unverified member2')


@pytest.fixture
def evil_member():
    """Require a evil_member user."""
    return _require_user('evil_member', 'Evil member')


@pytest.fixture
def no_perms_user():
    """Require a user with no permissions."""
    return _require_user('no_perms_member', 'User with no permissions')
