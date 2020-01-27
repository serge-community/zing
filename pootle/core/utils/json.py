# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.


import datetime
import json

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import dateformat
from django.utils.encoding import force_str


class PootleJSONEncoder(DjangoJSONEncoder):
    """Custom JSON encoder for Pootle.

    This is mostly implemented to avoid calling `force_str` all the time on
    certain types of objects.
    https://docs.djangoproject.com/en/1.4/topics/serialization/#id2
    """

    def default(self, obj):
        if (isinstance(obj, datetime.datetime) or
            isinstance(obj, datetime.date) or
            isinstance(obj, datetime.time)):
            return int(dateformat.format(obj, 'U'))

        try:
            return super(PootleJSONEncoder, self).default(obj)
        except TypeError:
            return force_str(obj)


def jsonify(obj, indent=None):
    """Serialize Python `obj` object into a JSON string."""
    if settings.DEBUG and indent is None:
        indent = 4

    return json.dumps(
        obj, indent=indent, cls=PootleJSONEncoder, sort_keys=True,
        separators=(',', ': ')
    )


def remove_empty_from_dict(input):
    """Removes empty (falsy) values from dictionaries recursively."""
    if not isinstance(input, dict):
        return input

    return {
        key: remove_empty_from_dict(value)
        for key, value in iter(input.items())
        if value and remove_empty_from_dict(value)
    }
