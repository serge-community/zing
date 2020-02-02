# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from django.core import checks
from django.db import OperationalError, ProgrammingError
from django.utils.translation import gettext as _


# XXX List of manage.py commands not to run the rqworker check on.
# Maybe tagging can improve this?
RQWORKER_WHITELIST = [
    "start",
    "initdb",
    "revision",
    "sync_stores",
    "refresh_stats",
    "update_stores",
    "calculate_checks",
    "retry_failed_jobs",
    "check",
    "runserver",
]


@checks.register()
def check_redis(app_configs=None, **kwargs):
    from django_rq.queues import get_queue
    from django_rq.workers import Worker

    errors = []

    try:
        queue = get_queue()
        Worker.all(queue.connection)
    except Exception as e:
        conn_settings = queue.connection.connection_pool.connection_kwargs
        errors.append(
            checks.Critical(
                _("Could not connect to Redis (%s)", e),
                hint=_("Make sure Redis is running on " "%(host)s:%(port)s")
                % conn_settings,
                id="pootle.C001",
            )
        )
    else:
        if len(queue.connection.smembers(Worker.redis_workers_keys)) == 0:
            # We need to check we're not running manage.py rqworker right now..
            import sys

            if len(sys.argv) > 1 and sys.argv[1] in RQWORKER_WHITELIST:
                errors.append(
                    checks.Warning(
                        _("No RQ Worker running."),
                        hint=_("Run new workers with manage.py rqworker"),
                        id="pootle.W001",
                    )
                )

    return errors


@checks.register()
def check_settings(app_configs=None, **kwargs):
    from django.conf import settings

    errors = []

    if "RedisCache" not in settings.CACHES.get("default", {}).get("BACKEND"):
        errors.append(
            checks.Critical(
                _("Cache backend is not set to Redis."),
                hint=_(
                    "Set default cache backend to "
                    "django_redis.cache.RedisCache\n"
                    "Current settings: %r" % (settings.CACHES.get("default"))
                ),
                id="pootle.C005",
            )
        )
    else:
        from django_redis import get_redis_connection

        if not get_redis_connection():
            errors.append(
                checks.Critical(
                    _("Could not initiate a Redis cache connection"),
                    hint=_("Double-check your CACHES settings"),
                    id="pootle.C004",
                )
            )

    redis_cache_aliases = ("default", "redis", "stats")
    redis_locations = set()
    for alias in redis_cache_aliases:
        if alias in settings.CACHES:
            redis_locations.add(settings.CACHES.get(alias, {}).get("LOCATION"))

    if len(redis_locations) < len(redis_cache_aliases):
        errors.append(
            checks.Critical(
                _(
                    "Distinct django_redis.cache.RedisCache configurations "
                    "are required for `default`, `redis` and `stats`."
                ),
                hint=_("Double-check your CACHES settings"),
                id="pootle.C017",
            )
        )

    if settings.DEBUG:
        errors.append(
            checks.Warning(
                _("DEBUG mode is on. Do not do this in production!"),
                hint=_("Set DEBUG = False in Zing settings"),
                id="pootle.W005",
            )
        )
    elif "sqlite" in settings.DATABASES.get("default", {}).get("ENGINE"):
        # We don't bother warning about sqlite in DEBUG mode.
        errors.append(
            checks.Warning(
                _("The sqlite database backend is unsupported"),
                hint=_("Set your default database engine to postgresql or mysql"),
                id="pootle.W006",
            )
        )

    if settings.SESSION_ENGINE.split(".")[-1] not in ("cache", "cached_db"):
        errors.append(
            checks.Warning(
                _("Not using cached_db as session engine"),
                hint=_(
                    "Set SESSION_ENGINE to "
                    "django.contrib.sessions.backend.cached_db\n"
                    "Current settings: %r" % (settings.SESSION_ENGINE)
                ),
                id="pootle.W007",
            )
        )

    if settings.ZING_CONTACT_EMAIL == "info@YOUR_DOMAIN.com":
        errors.append(
            checks.Warning(
                _(
                    "ZING_CONTACT_EMAIL is using the following default "
                    "setting %r." % settings.ZING_CONTACT_EMAIL
                ),
                hint=_(
                    "ZING_CONTACT_EMAIL is the address that will receive "
                    "messages sent by the contact form."
                ),
                id="pootle.W011",
            )
        )

    if not settings.DEFAULT_FROM_EMAIL:
        errors.append(
            checks.Warning(
                _("DEFAULT_FROM_EMAIL is not set."),
                hint=_(
                    "DEFAULT_FROM_EMAIL is used in all outgoing Zing email.\n"
                    "Don't forget to review your mail server settings."
                ),
                id="pootle.W009",
            )
        )

    if settings.DEFAULT_FROM_EMAIL in ("info@YOUR_DOMAIN.com", "webmaster@localhost"):
        errors.append(
            checks.Warning(
                _(
                    "DEFAULT_FROM_EMAIL is using the following default "
                    "setting %r." % settings.DEFAULT_FROM_EMAIL
                ),
                hint=_(
                    "DEFAULT_FROM_EMAIL is used in all outgoing Zing email.\n"
                    "Don't forget to review your mail server settings."
                ),
                id="pootle.W010",
            )
        )

    if settings.ZING_TM_SERVER:
        if "HOST" not in settings.ZING_TM_SERVER:
            errors.append(
                checks.Critical(
                    _("ZING_TM_SERVER has no HOST."),
                    hint=_("Set a HOST for ZING_TM_SERVER."),
                    id="pootle.C011",
                )
            )

        if "PORT" not in settings.ZING_TM_SERVER:
            errors.append(
                checks.Critical(
                    _("ZING_TM_SERVER has no PORT."),
                    hint=_("Set a PORT for ZING_TM_SERVER."),
                    id="pootle.C012",
                )
            )

        if "WEIGHT" in settings.ZING_TM_SERVER and not (
            0.0 <= settings.ZING_TM_SERVER["WEIGHT"] <= 1.0
        ):
            errors.append(
                checks.Warning(
                    _(
                        "ZING_TM_SERVER has a WEIGHT less than 0.0 or "
                        "greater than 1.0"
                    ),
                    hint=_(
                        "Set a WEIGHT between 0.0 and 1.0 (both included) "
                        "for ZING_TM_SERVER."
                    ),
                    id="pootle.W019",
                )
            )

    for coefficient_name in ["EDIT", "REVIEW", "SUGGEST", "ANALYZE"]:
        if coefficient_name not in settings.ZING_SCORE_COEFFICIENTS:
            errors.append(
                checks.Critical(
                    _("ZING_SCORE_COEFFICIENTS has no %s." % coefficient_name),
                    hint=_("Set %s in ZING_SCORE_COEFFICIENTS." % coefficient_name),
                    id="pootle.C014",
                )
            )
        else:
            coef = settings.ZING_SCORE_COEFFICIENTS[coefficient_name]
            if not isinstance(coef, float):
                errors.append(
                    checks.Critical(
                        _(
                            "Invalid value for %s in ZING_SCORE_COEFFICIENTS.",
                            coefficient_name,
                        ),
                        hint=_(
                            "Set a valid value for %s in ZING_SCORE_COEFFICIENTS.",
                            coefficient_name,
                        ),
                        id="pootle.C015",
                    )
                )

    return errors


@checks.register("data")
def check_users(app_configs=None, **kwargs):
    from django.contrib.auth import get_user_model

    errors = []

    User = get_user_model()
    try:
        admin_user = User.objects.get(username="admin")
    except (User.DoesNotExist, OperationalError, ProgrammingError):
        pass
    else:
        if admin_user.check_password("admin"):
            errors.append(
                checks.Warning(
                    _("The default 'admin' user still has a password set to 'admin'."),
                    hint=_("Remove the 'admin' user or change its password."),
                    id="pootle.W016",
                )
            )

    return errors


@checks.register()
def check_email_server_is_alive(app_configs=None, **kwargs):
    from django.conf import settings

    errors = []
    if settings.ZING_SIGNUP_ENABLED or settings.ZING_CONTACT_EMAIL.strip():
        from django.core.mail import get_connection

        connection = get_connection()
        try:
            connection.open()
        except Exception:
            errors.append(
                checks.Warning(
                    _("Email server is not available."),
                    hint=_(
                        "Review your email settings and make sure your email "
                        "server is working."
                    ),
                    id="pootle.W004",
                )
            )
        else:
            connection.close()
    return errors


@checks.register("data")
def check_revision(app_configs=None, **kwargs):
    from pootle.core.models import Revision
    from pootle_store.models import Unit

    errors = []
    revision = Revision.get()
    try:
        max_revision = Unit.max_revision()
    except (OperationalError, ProgrammingError):
        return errors
    if revision is None or revision < max_revision:
        errors.append(
            checks.Critical(
                _("Revision is missing or has an incorrect value."),
                hint=_("Run `revision --restore` to reset the revision counter."),
                id="pootle.C016",
            )
        )

    return errors
