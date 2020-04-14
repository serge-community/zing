# -*- coding: utf-8 -*-
#
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from functools import wraps


def disable_for_loaddata(signal_handler):
    """Decorator that turns off signal handlers when loading fixture data."""

    @wraps(signal_handler)
    def wrapper(*args, **kwargs):
        if kwargs.get("raw", False):
            return
        signal_handler(*args, **kwargs)

    return wrapper
