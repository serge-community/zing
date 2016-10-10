# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from __future__ import absolute_import

import json

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.encoding import force_unicode
from django.utils.functional import Promise

from ..markup import Markup


class PootleJSONEncoder(DjangoJSONEncoder):
    """Custom JSON encoder for Pootle.

    This is mostly implemented to avoid calling `force_unicode` all the time on
    certain types of objects.
    https://docs.djangoproject.com/en/1.4/topics/serialization/#id2
    """

    def default(self, obj):
        if isinstance(obj, (Promise, Markup)):
            return force_unicode(obj)

        return super(PootleJSONEncoder, self).default(obj)


def jsonify(obj):
    """Serialize Python `obj` object into a JSON string."""
    if settings.DEBUG:
        indent = 4
    else:
        indent = None

    return json.dumps(obj, indent=indent, cls=PootleJSONEncoder, sort_keys=True)


def clean_dict(obj):
    """Cleans values that evaluate to false (empty strings
    and zero values) since these can be easily dealt with
    on the client side; this is a recursive function that
    returns a new dictionary; it is expected for the dict
    structure to only contain primitive types (no objects)"""
    if isinstance(obj, dict):
        out = dict()
        for key in list(obj.keys()):
            iout = clean_dict(obj[key])
            if isinstance(obj[key], dict) and not len(iout.keys()):
                continue
            if isinstance(obj[key], list) and not len(iout):
                continue
            if iout:
                out[key] = iout
        return out
    elif isinstance(obj, list):
        out = list()
        for item in obj:
            iout = clean_dict(item)
            if iout:
                out.append(iout)
        return out
    else:
        return obj