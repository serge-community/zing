# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
#
# This file is a part of the Pootle project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import pytest

from django.core.management import call_command
from django.core.management.base import CommandError


@pytest.mark.cmd
@pytest.mark.django_db
def test_verify_user_nouser(capfd):
    with pytest.raises(CommandError) as e:
        call_command('verify_user')
    assert "Either provide a 'user' to verify or use '--all'" in str(e.value)


@pytest.mark.cmd
@pytest.mark.django_db
def test_verify_user_user_and_all(capfd):
    with pytest.raises(CommandError) as e:
        call_command('verify_user', '--all', 'member')
    assert "Either provide a 'user' to verify or use '--all'" in str(e.value)


@pytest.mark.cmd
@pytest.mark.django_db
def test_verify_user_unknownuser(capfd):
    with pytest.raises(CommandError) as e:
        call_command('verify_user', 'not_a_user')
    assert "User not_a_user does not exist" in str(e.value)


@pytest.mark.cmd
@pytest.mark.django_db
def test_verify_unverified(capfd, unverified_member):
    call_command('verify_user', 'unverified_member')
    out, err = capfd.readouterr()
    assert "User 'unverified_member' has been verified" in out


@pytest.mark.cmd
@pytest.mark.django_db
def test_verify_user_all(capfd, unverified_member, unverified_member2):
    call_command('verify_user', '--all')
    out, err = capfd.readouterr()
    assert "Verified user 'unverified_member'" in out
    assert "Verified user 'unverified_member2'" in out


@pytest.mark.cmd
@pytest.mark.django_db
def test_verify_user_multiple(capfd, unverified_member, unverified_member2):
    call_command('verify_user', 'unverified_member', 'unverified_member2')
    out, err = capfd.readouterr()
    assert "User 'unverified_member' has been verified" in out
    assert "User 'unverified_member2' has been verified" in out
