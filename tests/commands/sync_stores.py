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


@pytest.mark.cmd
@pytest.mark.django_db
def test_sync_stores_noargs(capfd, project0, project1):
    """Site wide sync_stores"""
    project0.delete()
    project1.delete()
    capfd.readouterr()
    call_command("sync_stores")
    out, err = capfd.readouterr()
    # FIXME we should work out how to get something here
    assert out == ""
    assert err == ""
