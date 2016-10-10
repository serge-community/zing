#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Pootle project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from django import template
from django.utils.safestring import mark_safe

from ..utils.docs import get_docs_url
from ..utils.json import jsonify


register = template.Library()


@register.filter
def to_js(value):
    """Returns a string which leaves the value readily available for JS
    consumption; breaks closing HTML tags into concatenated strings
    to avoid '</script> inside JS string' problem
    """
    return mark_safe(jsonify(value).replace('</', '</"+"'))


@register.filter
def docs_url(path_name):
    """Returns the absolute URL to `path_name` in the RTD docs."""
    return get_docs_url(path_name)
