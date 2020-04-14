# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import os
from collections import OrderedDict
from datetime import timedelta

from dateutil.relativedelta import relativedelta
from translate.storage.factory import getclass

from django.core.management import call_command


class PootleTestEnv(object):
    def __init__(self, data_file, *args, **kwargs):
        self.data_file = data_file

    def setup(self, request):
        """Setup test environment by trying to load a data dump file. If this is
        missing, populate the DB and generate the dump for use in future test runs.
        """
        data_file = self.data_file
        if os.path.isfile(data_file):
            self.setup_case_sensitive_schema()
            call_command("loaddata", data_file)
        else:
            self.setup_site_db(request)
            with open(data_file, "w") as file:
                call_command("dumpdata", "--indent=3", stdout=file)

    def setup_site_db(self, request, **kwargs):
        self.setup_redis()
        self.setup_case_sensitive_schema()
        self.setup_site_root()
        self.setup_languages()
        self.setup_site_matrix()
        self.setup_system_users(request)
        self.setup_permissions()
        self.setup_site_permissions()
        self.setup_tps()
        self.setup_disabled_project()
        self.setup_subdirs()
        self.setup_submissions()
        self.setup_terminology()
        self.setup_complex_po()

    def setup_complex_po(self):
        import tests
        from tests.factories import StoreDBFactory
        from pootle_translationproject.models import TranslationProject

        po_file = os.path.join(
            os.path.dirname(tests.__file__), *("data", "po", "complex.po")
        )
        with open(po_file, "rb") as f:
            ttk = getclass(f)(f.read())

        tp = TranslationProject.objects.get(
            project__code="project0", language__code="language0"
        )

        store = StoreDBFactory(
            parent=tp.directory, translation_project=tp, name="complex.po"
        )
        store.update(ttk)

    def setup_case_sensitive_schema(self):
        from django.db import connection
        from django.apps import apps
        from pootle.core.utils.db import set_mysql_collation_for_column

        if connection.vendor != "mysql":
            return

        cursor = connection.cursor()

        # Language
        set_mysql_collation_for_column(
            apps,
            cursor,
            "pootle_language.Language",
            "code",
            "utf8_general_ci",
            "varchar(50)",
        )

        # Project
        set_mysql_collation_for_column(
            apps, cursor, "pootle_project.Project", "code", "utf8_bin", "varchar(255)",
        )

        # Directory
        set_mysql_collation_for_column(
            apps,
            cursor,
            "pootle_app.Directory",
            "pootle_path",
            "utf8_bin",
            "varchar(255)",
        )
        set_mysql_collation_for_column(
            apps, cursor, "pootle_app.Directory", "name", "utf8_bin", "varchar(255)",
        )

        # Store
        set_mysql_collation_for_column(
            apps,
            cursor,
            "pootle_store.Store",
            "pootle_path",
            "utf8_bin",
            "varchar(255)",
        )
        set_mysql_collation_for_column(
            apps, cursor, "pootle_store.Store", "name", "utf8_bin", "varchar(255)",
        )

    def setup_permissions(self):
        from django.contrib.contenttypes.models import ContentType

        from .fixtures.models.permission import _require_permission

        args = {"app_label": "pootle_app", "model": "directory"}
        pootle_content_type = ContentType.objects.get(**args)

        _require_permission("view", "Can access a project", pootle_content_type)
        _require_permission("hide", "Cannot access a project", pootle_content_type)
        _require_permission("suggest", "Can make a suggestion", pootle_content_type)
        _require_permission("translate", "Can submit translations", pootle_content_type)
        _require_permission("review", "Can review translations", pootle_content_type)
        _require_permission(
            "administrate", "Can administrate a TP", pootle_content_type
        )

    def setup_languages(self):
        from .fixtures.models.language import _require_language

        _require_language("en", "English")

    def setup_redis(self):
        from pootle.core.models import Revision

        Revision.initialize(force=True)

    def setup_system_users(self, request):
        from .fixtures.models.user import TEST_USERS, _require_user

        users = OrderedDict(sorted(TEST_USERS.items()))
        for username, user_params in users.items():
            _require_user(username=username, request=request, **user_params)

    def setup_site_permissions(self):
        from django.contrib.auth import get_user_model

        from pootle_app.models import Directory, PermissionSet

        User = get_user_model()

        nobody = User.objects.get_nobody_user()
        default = User.objects.get_default_user()

        from django.contrib.auth.models import Permission

        view = Permission.objects.get(codename="view")
        suggest = Permission.objects.get(codename="suggest")
        translate = Permission.objects.get(codename="translate")

        criteria = {"user": nobody, "directory": Directory.objects.root}
        permission_set, created = PermissionSet.objects.get_or_create(**criteria)
        if created:
            permission_set.positive_permissions.set([view, suggest])
            permission_set.save()

        criteria["user"] = default
        permission_set, created = PermissionSet.objects.get_or_create(**criteria)
        if created:
            permission_set.positive_permissions.set([view, suggest, translate])
            permission_set.save()

    def setup_site_root(self):
        from tests.factories import DirectoryFactory

        DirectoryFactory(name="projects", parent=DirectoryFactory(parent=None, name=""))

    def setup_site_matrix(self):
        from tests.factories import ProjectDBFactory, LanguageDBFactory

        from pootle_language.models import Language

        # add 2 languages
        for i_ in range(0, 2):
            LanguageDBFactory()

        source_language = Language.objects.get(code="en")
        for i_ in range(0, 2):
            # add 2 projects
            ProjectDBFactory(source_language=source_language)

    def setup_terminology(self):
        from tests.factories import (
            ProjectDBFactory,
            StoreDBFactory,
            TranslationProjectFactory,
            UnitDBFactory,
        )
        from pootle_language.models import Language

        source_language = Language.objects.get(code="en")
        terminology = ProjectDBFactory(
            code="terminology",
            checkstyle="terminology",
            fullname="Terminology",
            source_language=source_language,
        )
        for language in Language.objects.exclude(code="en"):
            tp = TranslationProjectFactory(project=terminology, language=language)

            store = StoreDBFactory(translation_project=tp, name="terminology.po")
            store.save()
            for i_ in range(0, 1):
                UnitDBFactory(store=store)

    def setup_disabled_project(self):
        from tests.factories import (
            DirectoryFactory,
            ProjectDBFactory,
            TranslationProjectFactory,
        )

        from pootle_language.models import Language

        source_language = Language.objects.get(code="en")
        project = ProjectDBFactory(
            code="disabled_project0",
            fullname="Disabled Project 0",
            source_language=source_language,
        )
        project.disabled = True
        project.save()
        language = Language.objects.get(code="language0")
        tp = TranslationProjectFactory(project=project, language=language)
        tp_dir = tp.directory
        tp_dir.obsolete = False
        tp_dir.save()
        self._add_stores(tp, n=(1, 1))
        subdir0 = DirectoryFactory(name="subdir0", parent=tp.directory)
        self._add_stores(tp, n=(1, 1), parent=subdir0)

    def setup_subdirs(self):
        from tests.factories import DirectoryFactory

        from pootle_translationproject.models import TranslationProject

        for tp in TranslationProject.objects.all():
            subdir0 = DirectoryFactory(name="subdir0", parent=tp.directory)
            subdir1 = DirectoryFactory(name="subdir1", parent=subdir0)
            self._add_stores(tp, n=(2, 1), parent=subdir0)
            self._add_stores(tp, n=(1, 1), parent=subdir1)

            # Create empty dir and imitate file scanning, which will make the
            # directory obsolete
            empty_dir0 = DirectoryFactory(name="empty_dir0", parent=tp.directory)
            empty_dir0.makeobsolete()
            # The other "empty" directory contains an store with no units
            empty_dir1 = DirectoryFactory(name="empty_dir1", parent=tp.directory)
            self._add_stores(tp, n=(1, 0), parent=empty_dir1)

    def setup_submissions(self):
        from pootle_store.models import Store, Unit
        from django.utils import timezone

        year_ago = timezone.now() - relativedelta(years=1)
        Unit.objects.update(creation_time=year_ago)

        stores = Store.objects.select_related(
            "translation_project__project", "translation_project__language"
        )

        for store in stores.all():
            for unit in store.unit_set.all():
                unit.store = store
                self._add_submissions(unit, year_ago)

    def setup_tps(self):
        from pootle_project.models import Project
        from pootle_language.models import Language
        from tests.factories import TranslationProjectFactory

        for project in Project.objects.all():
            for language in Language.objects.exclude(code="en"):
                # add a TP to the project for each language
                tp = TranslationProjectFactory(project=project, language=language)
                # As there are no files on the FS we have to currently unobsolete
                # the directory
                tp_dir = tp.directory
                tp_dir.obsolete = False
                tp_dir.save()
                self._add_stores(tp)

    def _add_stores(self, tp, n=(3, 2), parent=None):
        from tests.factories import StoreDBFactory, UnitDBFactory

        from pootle_store.constants import UNTRANSLATED, TRANSLATED, FUZZY, OBSOLETE

        for i_ in range(0, n[0]):
            # add 3 stores
            if parent is None:
                store = StoreDBFactory(translation_project=tp)
            else:
                store = StoreDBFactory(translation_project=tp, parent=parent)
            store.save()

            # add 8 units to each store
            for state in [UNTRANSLATED, TRANSLATED, FUZZY, OBSOLETE]:
                for i_ in range(0, n[1]):
                    UnitDBFactory(store=store, state=state)

    def _update_submission_times(self, unit, update_time, last_update=None):
        submissions = unit.submission_set.all()
        if last_update:
            submissions = submissions.exclude(creation_time__lte=last_update)
        submissions.update(creation_time=update_time)

    def _add_submissions(self, unit, created):
        from pootle_statistics.models import SubmissionTypes
        from pootle_store.constants import UNTRANSLATED, FUZZY, OBSOLETE
        from pootle_store.models import Unit

        from django.contrib.auth import get_user_model
        from django.utils import timezone

        original_state = unit.state
        unit.created = created

        User = get_user_model()
        admin = User.objects.get(username="admin")
        member = User.objects.get(username="member")
        member2 = User.objects.get(username="member2")

        first_modified = created + relativedelta(months=unit.index, days=10)

        # add suggestion at first_modified
        suggestion, created_ = unit.add_suggestion(
            "Suggestion for %s" % (unit.target or unit.source), user=member, touch=False
        )
        self._update_submission_times(unit, first_modified, created)

        # accept the suggestion 7 days later if not untranslated
        next_time = first_modified + timedelta(days=7)
        if original_state == UNTRANSLATED:
            unit.reject_suggestion(suggestion, unit.store.translation_project, admin)
        else:
            unit.accept_suggestion(suggestion, unit.store.translation_project, admin)
            Unit.objects.filter(pk=unit.pk).update(
                submitted_on=next_time, mtime=next_time
            )
        self._update_submission_times(unit, next_time, first_modified)

        # add another suggestion as different user 7 days later
        suggestion2_, created_ = unit.add_suggestion(
            "Suggestion 2 for %s" % (unit.target or unit.source),
            user=member2,
            touch=False,
        )
        self._update_submission_times(
            unit, first_modified + timedelta(days=14), next_time
        )

        # mark FUZZY
        if original_state == FUZZY:
            unit.markfuzzy()

        # mark OBSOLETE
        elif original_state == OBSOLETE:
            unit.makeobsolete()

        elif unit.target:
            # Re-edit units with translations, adding some submissions
            # of SubmissionTypes.EDIT_TYPES
            old_target = unit.target
            old_state = unit.state
            current_time = timezone.now() - timedelta(days=14)

            unit.target_f = "Updated %s" % old_target
            unit._target_updated = True
            unit.store.record_submissions(
                unit,
                old_target,
                old_state,
                current_time,
                member,
                SubmissionTypes.NORMAL,
            )

        unit.save()
