# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Pootle project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

"""
Pootle App Config
See https://docs.djangoproject.com/en/1.8/ref/applications/
"""

from django.apps import AppConfig


class PootleConfig(AppConfig):
    name = "pootle_app"
    verbose_name = "Pootle"

    def ready(self):
        from pootle import checks  # noqa
