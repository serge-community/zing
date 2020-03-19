# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from django.db import models

from .constants import LANGUAGE_REGEX, OBSOLETE, PROJECT_REGEX
from .util import SuggestionStates


class SuggestionManager(models.Manager):
    def pending(self):
        return self.get_queryset().filter(state=SuggestionStates.PENDING)


class UnitManager(models.Manager):
    def live(self):
        """Filters non-obsolete units."""
        return self.filter(state__gt=OBSOLETE)

    def get_for_user(self, user, include_disabled=False):
        """Filters units for a specific user.

        - Admins always get all non-obsolete units, optionally filtered to
            include units from disabled projects too.
        - Regular users only get units from enabled projects accessible
            to them.

        :param user: The user for whom units need to be retrieved for.
        :param include_disabled: whether to include units from disabled
            projects or not. This only affects superusers.
        :return: A filtered queryset with `Unit`s for `user`.
        """
        from pootle_project.models import Project

        if user.is_superuser:
            if include_disabled:
                return self.live()
            return self.live().filter(
                store__translation_project__project__disabled=False
            )

        user_projects = Project.accessible_by_user(user)
        filter_by = {
            "store__translation_project__project__disabled": False,
            "store__translation_project__project__code__in": user_projects,
        }
        return self.live().filter(**filter_by)

    def get_translatable(
        self,
        user,
        project_code=None,
        language_code=None,
        dir_path=None,
        filename=None,
        include_disabled=False,
    ):
        """Returns translatable units for a `user`, optionally filtered by their
        location within Pootle.

        :param user: The user who is accessing the units.
        :param project_code: A string for matching the code of a Project.
        :param language_code: A string for matching the code of a Language.
        :param dir_path: A string for matching the dir_path and descendants
           from the TP.
        :param filename: A string for matching the filename of Stores.
        :param include_disabled: whether to include units from disabled
            projects or not. This affects admin users only.
        """

        units_qs = self.get_for_user(user, include_disabled=include_disabled)

        if language_code:
            units_qs = units_qs.filter(
                store__translation_project__language__code=language_code,
            )

        if project_code:
            units_qs = units_qs.filter(
                store__translation_project__project__code=project_code
            )

        if not (dir_path or filename):
            return units_qs

        pootle_path = "/%s/%s/%s%s" % (
            language_code or LANGUAGE_REGEX,
            project_code or PROJECT_REGEX,
            dir_path or "",
            filename or "",
        )
        if language_code and project_code:
            if filename:
                return units_qs.filter(store__pootle_path=pootle_path)
            else:
                return units_qs.filter(store__pootle_path__startswith=pootle_path)
        else:
            # we need to use a regex in this case as lang or proj are not
            # set
            if filename:
                pootle_path = "%s$" % pootle_path
            return units_qs.filter(store__pootle_path__regex=pootle_path)


class StoreManager(models.Manager):
    def live(self):
        """Filters non-obsolete stores."""
        return self.filter(obsolete=False)

    def create(self, *args, **kwargs):
        kwargs["pootle_path"] = "%s%s" % (kwargs["parent"].pootle_path, kwargs["name"])
        return super().create(*args, **kwargs)
