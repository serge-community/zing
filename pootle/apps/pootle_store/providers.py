# -*- coding: utf-8 -*-
#
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from pootle.core.delegate import format_syncers, format_updaters
from pootle.core.plugin import provider

from .syncer import StoreSyncer
from .updater import StoreUpdater


@provider(format_syncers)
def register_format_syncers(**kwargs_):
    return dict(
        default=StoreSyncer)


@provider(format_updaters)
def register_format_updaters(**kwargs_):
    return dict(default=StoreUpdater)
