# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import pytest

from django.core.management import call_command
from django.core.management.base import CommandError


@pytest.mark.cmd
@pytest.mark.django_db
def test_update_tmserver_nosetting(capfd, po_directory, tp0):
    """We need configured TM for anything to work"""
    with pytest.raises(CommandError) as e:
        call_command('update_tmserver')
    assert "POOTLE_TM_SERVER setting is missing." in str(e)


@pytest.mark.cmd
@pytest.mark.django_db
def __test_update_tmserver_noargs(capfd, tp0, settings):
    """Load TM from the database"""

    from pootle_store.models import Unit

    units_qs = (
        Unit.objects
            .exclude(target_f__isnull=True)
            .exclude(target_f__exact=''))

    settings.POOTLE_TM_SERVER = {
        'HOST': 'localhost',
        'PORT': 9200,
    }
    call_command('update_tmserver')
    out, err = capfd.readouterr()
    assert "Last indexed revision = -1" in out

    assert ("%d translations to index" % units_qs.count()) in out
