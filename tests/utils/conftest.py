import os

import pytest


def pytest_collection_modifyitems(items):
    """Adds the `django_db` marker for tests that use the `settings` fixture,
    modify timezone-related settings and run in PostgreSQL.

    This is required because Django resets the DB connection settings upon
    changing `USE_TZ` or `TIME_ZONE` settings.

    Refs.
    https://docs.djangoproject.com/en/1.11/topics/testing/tools/#django.test.modify_settings
    """
    # Note: this is tied to our Travis + Tox configuration
    has_postgres = os.environ.get('DATABASE_BACKEND', '') == 'postgres'
    if not has_postgres:
        return

    for item in items:
        if 'settings' not in item.fixturenames:
            continue

        code = item.function.func_code
        if 'settings' not in code.co_varnames:
            # `settings` not being modified, skip
            continue

        if 'USE_TZ' in code.co_names or 'TIME_ZONE' in code.co_names:
            item.add_marker(pytest.mark.django_db)
