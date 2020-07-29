# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from django.contrib.auth import get_user_model
from django.core.validators import ValidationError

import pytest

from allauth.account.models import EmailAddress

from tests.fixtures.models.store import (
    _create_submission_and_suggestion,
    _create_comment_on_unit,
)

import accounts

from pootle_app.models.permissions import PermissionSet
from pootle_store.constants import FUZZY, TRANSLATED


def _make_evil_member_updates(store, evil_member):
    # evil_member makes following changes:
    #   - rejects member's suggestion on unit
    #   - changes unit
    #   - adds another suggestion on unit
    #   - accepts their own suggestion
    #   - adds a comment on unit
    #   - adds another unit
    member_suggestion = store.units[0].get_suggestions().first()
    evil_units = [
        ("Hello, world", "Hello, world EVIL"),
        ("Goodbye, world", "Goodbye, world EVIL"),
    ]
    unit = store.units[0]
    unit.reject_suggestion(
        member_suggestion, store.units[0].store.translation_project, evil_member
    )
    _create_submission_and_suggestion(
        store, evil_member, units=evil_units, suggestion="EVIL SUGGESTION"
    )
    evil_suggestion = store.units[0].get_suggestions().first()
    store.units[0].accept_suggestion(
        evil_suggestion, store.units[0].store.translation_project, evil_member
    )
    _create_comment_on_unit(store.units[0], evil_member, "EVIL COMMENT")


def _test_user_merged(unit, src_user, target_user):
    # TODO: test reviews and comments
    if src_user.id:
        assert src_user.submitted.count() == 0
        assert src_user.suggestions.count() == 0

    assert unit in list(target_user.submitted.all())
    assert unit.get_suggestions().first() in list(target_user.suggestions.all())


def _test_before_evil_user_updated(store, member, teststate=False):
    unit = store.units[0]

    # Unit state is fuzzy
    assert unit.state == FUZZY

    # Unit target was updated.
    assert unit.target_f == "Hello, world UPDATED"
    assert unit.submitted_by == member

    # But member also added a suggestion to the unit.
    assert unit.get_suggestions().count() == 1
    assert unit.get_suggestions().first().user == member

    # And added a comment on the unit.
    assert unit.translator_comment == "NICE COMMENT"
    assert unit.commented_by == member

    # Only 1 unit round here.
    assert store.units.count() == 1


def _test_after_evil_user_updated(store, evil_member):
    unit = store.units[0]

    # Unit state is TRANSLATED
    assert unit.state == TRANSLATED

    # Evil member has accepted their own suggestion.
    assert unit.target_f == "EVIL SUGGESTION"
    assert unit.submitted_by == evil_member

    # And rejected member's.
    assert unit.get_suggestions().count() == 0

    # And added their own comment.
    assert unit.translator_comment == "EVIL COMMENT"
    assert unit.commented_by == evil_member

    # Evil member has added another unit.
    assert store.units.count() == 2
    assert store.units[1].target_f == "Goodbye, world EVIL"
    assert store.units[1].submitted_by == evil_member


def _test_user_purging(store, member, evil_member, purge):

    first_revision = store.get_max_unit_revision()
    unit = store.units[0]

    # Get intitial change times
    initial_submission_time = unit.submitted_on
    initial_comment_time = unit.commented_on
    initial_review_time = unit.reviewed_on

    # Test state before evil user has updated.
    _test_before_evil_user_updated(store, member, True)

    # Update as evil member
    _make_evil_member_updates(store, evil_member)

    # Revision has increased
    latest_revision = store.get_max_unit_revision()
    assert latest_revision > first_revision

    unit = store.units[0]

    # Test submitted/commented/reviewed times on the unit.  This is an
    # unreliable test on MySQL due to datetime precision
    if unit.submitted_on.time().microsecond != 0:

        # Times have changed
        assert unit.submitted_on != initial_submission_time
        assert unit.commented_on != initial_comment_time
        assert unit.reviewed_on != initial_review_time

    # Test state after evil user has updated.
    _test_after_evil_user_updated(store, evil_member)

    # Purge evil_member
    purge(evil_member)

    # Revision has increased again.
    assert store.get_max_unit_revision() > latest_revision

    unit = store.units[0]

    # Times are back to previous times - by any precision
    assert unit.submitted_on == initial_submission_time.replace(microsecond=0)
    assert unit.commented_on == initial_comment_time.replace(microsecond=0)
    assert unit.reviewed_on == initial_review_time

    # State is be back to how it was before evil user updated.
    _test_before_evil_user_updated(store, member)


@pytest.mark.django_db
def test_merge_user(en_tutorial_po, member, member2):
    """Test merging user to another user."""
    unit = _create_submission_and_suggestion(en_tutorial_po, member)
    accounts.utils.UserMerger(member, member2).merge()
    _test_user_merged(unit, member, member2)


@pytest.mark.django_db
def test_delete_user(en_tutorial_po):
    """Test default behaviour of User.delete - merge to nobody"""
    User = get_user_model()

    member = User.objects.get(username="member")
    nobody = User.objects.get(username="nobody")
    unit = _create_submission_and_suggestion(en_tutorial_po, member)
    member.delete()
    _test_user_merged(unit, member, nobody)


@pytest.mark.django_db
def test_purge_user(en_tutorial_po_member_updated, member, evil_member):
    """Test purging user using `purge_user` function"""
    _test_user_purging(
        en_tutorial_po_member_updated,
        member,
        evil_member,
        lambda m: accounts.utils.UserPurger(m).purge(),
    )


@pytest.mark.django_db
def test_delete_purge_user(en_tutorial_po_member_updated, member, evil_member):
    """Test purging user using `User.delete(purge=True)`"""
    _test_user_purging(
        en_tutorial_po_member_updated,
        member,
        evil_member,
        lambda m: m.delete(purge=True),
    )


@pytest.mark.django_db
def test_verify_user_duplicate_email(trans_member, member):
    """Test verifying user using `verify_user` function"""

    # trans_member steals member's email
    trans_member.email = member.email

    # And can't verify with it
    with pytest.raises(ValidationError):
        accounts.utils.verify_user(trans_member)

    # Email not verified
    with pytest.raises(EmailAddress.DoesNotExist):
        EmailAddress.objects.get(user=trans_member, primary=True, verified=True)


@pytest.mark.django_db
def test_verify_user_with_primary_and_non_primary_email_object(trans_member):
    """Test verifying user using `verify_user` function that has an
    allauth.EmailAddress object but is not yet verified
    """
    member = trans_member

    # Give member an email
    member.email = "member@this.test"

    # Create the unverified non-primary email object
    EmailAddress.objects.create(
        user=member, email=member.email, primary=False, verified=False
    )

    # Create unverified primary email object
    EmailAddress.objects.create(
        user=member, email="otheremail@this.test", primary=True, verified=False
    )

    # Verify user
    accounts.utils.verify_user(member)

    # Get the verified email object - the primary address is used
    EmailAddress.objects.get(
        user=member, email="otheremail@this.test", primary=True, verified=True
    )


@pytest.mark.django_db
def test_verify_user_already_verified(unverified_member):
    """Test verifying user using `verify_user` function that has an
    allauth.EmailAddress object but is not yet verified
    """
    # Verify user
    accounts.utils.verify_user(unverified_member)

    # Verify user again - raises ValueError
    with pytest.raises(ValueError):
        accounts.utils.verify_user(unverified_member)

    # Get the verified email object
    EmailAddress.objects.get(
        user=unverified_member,
        email=unverified_member.email,
        primary=True,
        verified=True,
    )


@pytest.mark.django_db
def test_user_has_manager_permissions(no_perms_user, administrate, tp0):
    """Test user `has_manager_permissions` method."""
    language0 = tp0.language
    project0 = tp0.project

    # User has no permissions, so can't be manager.
    assert not no_perms_user.has_manager_permissions()

    # Assign 'administrate' right for 'Language0 (Project0)' TP and check user
    # is manager.
    criteria = {
        "user": no_perms_user,
        "directory": tp0.directory,
    }
    ps = PermissionSet.objects.get_or_create(**criteria)[0]
    ps.positive_permissions.set([administrate])
    ps.save()
    assert no_perms_user.has_manager_permissions()
    ps.positive_permissions.clear()
    assert not no_perms_user.has_manager_permissions()

    # Assign 'administrate' right for 'Language0' and check user is manager.
    criteria["directory"] = language0.directory
    ps = PermissionSet.objects.get_or_create(**criteria)[0]
    ps.positive_permissions.set([administrate])
    ps.save()
    assert no_perms_user.has_manager_permissions()
    ps.positive_permissions.clear()
    assert not no_perms_user.has_manager_permissions()

    # Assign 'administrate' right for 'Project0' and check user is manager.
    criteria["directory"] = project0.directory
    ps = PermissionSet.objects.get_or_create(**criteria)[0]
    ps.positive_permissions.set([administrate])
    ps.save()
    assert no_perms_user.has_manager_permissions()
    ps.positive_permissions.clear()
    assert not no_perms_user.has_manager_permissions()
