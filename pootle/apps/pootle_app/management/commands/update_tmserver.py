# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import os
import sys
from hashlib import md5

# This must be run before importing Django.
os.environ["DJANGO_SETTINGS_MODULE"] = "pootle.settings"

from elasticsearch import Elasticsearch, helpers

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from pootle.core.utils import dateformat
from pootle_store.models import Unit


BULK_CHUNK_SIZE = 5000


class DBParser(object):
    def __init__(self, *args, **kwargs):
        self.stdout = kwargs.pop("stdout")
        self.INDEX_NAME = kwargs.pop("index", None)
        self.exclude_disabled_projects = not kwargs.pop("disabled_projects")

    def get_units(self):
        """Gets the units to import and its total count."""
        units_qs = (
            Unit.simple_objects.exclude(target_f__isnull=True)
            .exclude(target_f__exact="")
            .filter(revision__gt=self.last_indexed_revision)
            .select_related(
                "submitted_by",
                "store",
                "store__translation_project__project",
                "store__translation_project__language",
            )
        )

        if self.exclude_disabled_projects:
            units_qs = units_qs.exclude(
                store__translation_project__project__disabled=True
            )

        units_qs = units_qs.values(
            "id",
            "revision",
            "source_f",
            "target_f",
            "submitted_on",
            "submitted_by__username",
            "submitted_by__full_name",
            "submitted_by__email",
            "store__translation_project__project__fullname",
            "store__pootle_path",
            "store__translation_project__language__code",
        ).order_by()

        return units_qs.iterator(), units_qs.count()

    def get_unit_data(self, unit):
        """Return dict with data to import for a single unit."""
        fullname = unit["submitted_by__full_name"] or unit["submitted_by__username"]

        email_md5 = None
        if unit["submitted_by__email"]:
            email_md5 = md5(unit["submitted_by__email"].encode("utf-8")).hexdigest()

        mtime = None
        if unit["submitted_on"]:
            mtime = int(dateformat.format(unit["submitted_on"], "U"))

        index_name = unit["store__translation_project__language__code"].lower()
        return {
            "_index": index_name,
            "_id": unit["id"],
            "revision": unit["revision"],
            "project": unit["store__translation_project__project__fullname"],
            "path": unit["store__pootle_path"],
            "username": unit["submitted_by__username"],
            "fullname": fullname,
            "email_md5": email_md5,
            "source": unit["source_f"],
            "target": unit["target_f"],
            "mtime": mtime,
        }


class Command(BaseCommand):
    help = "Load Translation Memory with translations"

    def add_arguments(self, parser):
        parser.add_argument(
            "--refresh",
            action="store_true",
            dest="refresh",
            default=False,
            help="Process all items, not just the new ones, so "
            "existing translations are refreshed",
        )
        parser.add_argument(
            "--rebuild",
            action="store_true",
            dest="rebuild",
            default=False,
            help="Drop the entire TM on start and update everything from scratch",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            dest="dry_run",
            default=False,
            help="Report the number of translations to index and quit",
        )
        parser.add_argument(
            "--include-disabled-projects",
            action="store_true",
            dest="disabled_projects",
            default=False,
            help="Add translations from disabled projects",
        )

    def _parse_translations(self, **options):
        units, total = self.parser.get_units()

        if total == 0:
            self.stdout.write("No translations to index")
            sys.exit()

        self.stdout.write("%s translations to index" % total)

        if options["dry_run"]:
            sys.exit()

        self.stdout.write("")

        i = 0
        for i, unit in enumerate(units, start=1):
            if (i % 1000 == 0) or (i == total):
                percent = "%.1f" % (i * 100.0 / total)
                self.stdout.write("%s (%s%%)" % (i, percent), ending="\r")
                self.stdout.flush()

            yield self.parser.get_unit_data(unit)

        if i != total:
            self.stdout.write("Expected %d, loaded %d." % (total, i))

    def _initialize(self, **options):
        if not settings.ZING_TM_SERVER:
            raise CommandError("ZING_TM_SERVER setting is missing.")

        tm_settings = settings.ZING_TM_SERVER

        self.INDEX_NAME = tm_settings["INDEX_NAME"]

        self.es = Elasticsearch(
            [{"host": tm_settings["HOST"], "port": tm_settings["PORT"]}],
            retry_on_timeout=True,
        )

        self.parser = DBParser(
            stdout=self.stdout,
            index=self.INDEX_NAME,
            disabled_projects=options["disabled_projects"],
        )

    def _set_latest_indexed_revision(self, **options):
        self.last_indexed_revision = -1

        if (
            not options["rebuild"]
            and not options["refresh"]
            and self.es.indices.exists(self.INDEX_NAME)
        ):

            result = self.es.search(
                index=self.INDEX_NAME,
                body={"aggs": {"max_revision": {"max": {"field": "revision"}}}},
            )
            self.last_indexed_revision = (
                result["aggregations"]["max_revision"]["value"] or -1
            )

        self.parser.last_indexed_revision = self.last_indexed_revision

        self.stdout.write("Last indexed revision = %s" % self.last_indexed_revision)

    def handle(self, **options):
        self._initialize(**options)

        if (
            options["rebuild"]
            and not options["dry_run"]
            and self.es.indices.exists(self.INDEX_NAME)
        ):

            self.es.indices.delete(index=self.INDEX_NAME)

        if not options["dry_run"] and not self.es.indices.exists(self.INDEX_NAME):

            self.es.indices.create(index=self.INDEX_NAME)

        self._set_latest_indexed_revision(**options)

        helpers.bulk(self.es, self._parse_translations(**options))
