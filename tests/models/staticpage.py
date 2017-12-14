# -*- coding: utf-8 -*-
#
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from pytest_pootle.factories import StaticPageFactory


def test_staticpage_repr():
    staticpage = StaticPageFactory.build(virtual_path='/test/')
    assert '<StaticPage: /test/>' == repr(staticpage)
