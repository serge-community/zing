# -*- coding: utf-8 -*-
#
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import pytest

from pytest_pootle.factories import StaticPageFactory


def test_staticpage_repr():
    staticpage = StaticPageFactory.build(virtual_path='/test/')
    assert '<StaticPage: /test/>' == repr(staticpage)


@pytest.mark.django_db
def test_staticpage_save_with_changes():
    """Tests a static page's timestamp is updated upon saving changes (#316)."""
    page = StaticPageFactory.build(virtual_path='/test/', title='foo')
    page.save()

    page.title = 'bar'
    assert page.has_changes()

    old_mtime = page.modified_on
    page.save()

    assert page.modified_on != old_mtime
