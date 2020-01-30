#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
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
    return mark_safe(jsonify(value).replace("</", "<\\/"))


@register.filter
def to_jquery_safe_js(value):
    """Returns a string which leaves the value readily available for JS
    consumption; escapes closing tags to avoid '</script> inside JS string'
    problem; breaks HTML tags into concatenated strings to avoid jQuery `html()`
    rendering problem (see https://github.com/evernote/zing/issues/105).

    This template tag needs to be removed once the editor is moved into a native
    React component
    """
    return mark_safe(jsonify(value).replace("</", "<\\/").replace("<", '<"+"'))


@register.filter
def docs_url(path_name):
    """Returns the absolute URL to `path_name` in the RTD docs."""
    return get_docs_url(path_name)
