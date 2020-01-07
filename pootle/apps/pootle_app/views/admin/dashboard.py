# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from redis.exceptions import ConnectionError
from rq.registry import FailedJobRegistry

from django.shortcuts import render

from django_rq.queues import get_queue
from django_rq.workers import Worker

from pootle.core.decorators import admin_required
from pootle.i18n.gettext import ugettext as _, ungettext


def rq_stats():
    queue = get_queue()
    try:
        workers = Worker.all(queue.connection)
    except ConnectionError:
        return None

    num_workers = len(workers)
    is_running = len(queue.connection.smembers(Worker.redis_workers_keys)) > 0
    if is_running:
        # Translators: this refers to the status of the background job worker
        status_msg = ungettext('Running (%d worker)', 'Running (%d workers)',
                               num_workers) % num_workers
    else:
        # Translators: this refers to the status of the background job worker
        status_msg = _('Stopped')

    failed_job_registry = FailedJobRegistry(queue.name, queue.connection)
    result = {
        'job_count': queue.count,
        'failed_job_count': len(failed_job_registry),
        'is_running': is_running,
        'status_msg': status_msg,
    }

    return result


def checks():
    from django.core.checks.registry import registry

    return registry.run_checks()


@admin_required
def view(request):
    ctx = {
        'page': 'admin-dashboard',
        'rq_stats': rq_stats(),
        'checks': checks(),
    }
    return render(request, "admin/dashboard.html", ctx)
