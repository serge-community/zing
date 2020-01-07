# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import os

# This must be run before importing Django.
os.environ['DJANGO_SETTINGS_MODULE'] = 'pootle.settings'

from django.core.management.base import BaseCommand

from django_rq.queues import get_queue

from rq.registry import FailedJobRegistry


class Command(BaseCommand):
    help = "Retry failed RQ jobs."

    def handle(self, **options):
        queue = get_queue()
        failed_job_registry = FailedJobRegistry(queue.name, queue.connection)
        for job_id in failed_job_registry.get_job_ids():
            failed_job_registry.requeue(job_id)
