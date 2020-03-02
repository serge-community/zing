# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
#
# This file is a part of the Pootle project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import logging
import os

# This must be run before importing Django.
os.environ["DJANGO_SETTINGS_MODULE"] = "pootle.settings"

from pootle_store.models import Store

from . import PootleCommand


logger = logging.getLogger("stats")


class Command(PootleCommand):
    help = "Allow stats and text indices to be refreshed manually."
    process_disabled_projects = False

    def add_arguments(self, parser):
        super().add_arguments(parser)

        parser.add_argument(
            "--include-disabled-projects",
            action="store_true",
            dest="disabled_projects",
            default=False,
            help="Process disabled projects",
        )

    def handle_all(self, **options):
        self.__class__.process_disabled_projects = options["disabled_projects"]

        super().handle_all(**options)

    def handle_all_stores(self, translation_project, **options_):
        stores = Store.objects.live().filter(translation_project=translation_project)
        for store in stores.iterator():
            logger.info("Add job to update stats for %s", store.pootle_path)
            store.update_all_cache()
