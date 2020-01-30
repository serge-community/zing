# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Pootle project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import calendar
from datetime import datetime
from functools import wraps
from importlib import import_module

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseBadRequest
from django.utils import timezone


def import_func(path):
    i = path.rfind(".")
    module, attr = path[:i], path[i + 1 :]
    try:
        mod = import_module(module)
    except ImportError as e:
        raise ImproperlyConfigured('Error importing module %s: "%s"' % (module, e))
    try:
        func = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured(
            'Module "%s" does not define a "%s" callable function' % (module, attr)
        )

    return func


def dictsum(x, y):
    return dict((n, x.get(n, 0) + y.get(n, 0)) for n in set(x) | set(y))


def ajax_required(f):
    """Check that the request is an AJAX request.

    Use it in your views:

    @ajax_required
    def my_view(request):
        ....

    Taken from:
    http://djangosnippets.org/snippets/771/
    """

    @wraps(f)
    def wrapper(request, *args, **kwargs):
        if not settings.DEBUG and not request.is_ajax():
            return HttpResponseBadRequest("This must be an AJAX request.")
        return f(request, *args, **kwargs)

    return wrapper


def get_max_month_datetime(dt):
    """Returns the datetime representing the last second of the month with
    respect to the `dt` aware datetime.
    """
    days_in_month = calendar.monthrange(dt.year, dt.month)[1]

    tz = timezone.get_default_timezone()
    new_dt = tz.normalize(dt.replace(day=days_in_month),)

    # DST adjustments could have shifted the month or day
    if new_dt.month != dt.month:
        new_dt = new_dt.replace(month=dt.month)
    if new_dt.day != days_in_month:
        new_dt = new_dt.replace(day=days_in_month)

    return new_dt.replace(hour=23, minute=59, second=59, microsecond=0)


def get_date_interval(month):
    from pootle.core.utils.timezone import make_aware

    now = start = end = timezone.now()
    default_month = now.strftime("%Y-%m")

    if month is None:
        month = default_month

    try:
        month_datetime = datetime.strptime(month, "%Y-%m")
    except ValueError:
        month_datetime = datetime.strptime(default_month, "%Y-%m")

    start = make_aware(month_datetime)

    if start < now:
        if start.month != now.month or start.year != now.year:
            end = get_max_month_datetime(start)
    else:
        end = start

    start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    end = end.replace(hour=23, minute=59, second=59, microsecond=0)

    return [start, end]
