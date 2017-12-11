# -*- coding: utf-8 -*-
#
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import os

from django.template import RequestContext
from django.test.utils import ContextList
from django.utils.functional import cached_property

from pootle.core.utils.json import jsonify
from pootle.core.utils.list import flatten


# List of keys to filter out from a response context
BLACKLISTED_KEYS = [
    # Django template language-specific context
    'block', 'forloop', 'False', 'True', 'None',
    # More Django stuff
    'request', 'perms', 'csrf_token',
    # i18n context
    'LANGUAGES', 'LANGUAGE_BIDI', 'LANGUAGE_CODE',
    # Static and settings context
    'MEDIA_URL', 'STATIC_URL',
    # Zing context processors
    'settings', 'custom', 'display_agreement',
    'ALL_LANGUAGES', 'ALL_PROJECTS', 'SOCIAL_AUTH_PROVIDERS',

    # These context data keys are conflicting because they are auto-added by
    # Django after saving a model (`auto_now_add=True`), and hence they will
    # always differ across test runs. Until we find a better solution, we
    # need to filter them out here.
    'lastupdated',
    # Taken out due to its dynamic nature (#177)
    'top_scorers',
    # Taken out until we are able to `reset_sequences` (pytest-django/#308)
    'id',
    'due_date_id',
]


class Snapshot(object):

    def __init__(self, ctx_name, data_dir=None, generate=False, **kwargs):
        self.filename = '%s.json' % ctx_name
        self.data_dir = data_dir or ''
        self.generate = generate

    @cached_property
    def filepath(self):
        base_dir = os.path.normpath(self.data_dir)
        filepath = os.path.abspath(os.path.join(base_dir, self.filename))

        if os.path.commonprefix([filepath, base_dir]) != base_dir:
            raise ValueError(
                'The requested file path "%s" is out '
                'of the data directory "%s".' % (filepath, self.data_dir)
            )
        return filepath

    @cached_property
    def reference(self):
        try:
            with open(self.filepath) as reference_file:
                return reference_file.read()
        except IOError:
            return None

    def clean(self, data):
        """Cleans up `data` before using it as a snapshot reference."""
        if isinstance(data, RequestContext):
            return self.clean(data.flatten())
        # XXX: maybe we can do something smarter than blacklisting when we
        # have a `ContextList`?
        elif isinstance(data, dict) or isinstance(data, ContextList):
            return {
                key: self.clean(data[key]) for key in data.keys()
                if key not in BLACKLISTED_KEYS
            }
        elif isinstance(data, list):
            return [self.clean(item) for item in data]
        return data

    def serialize(self, ctx_data):
        return jsonify(self.clean(ctx_data), indent=2)

    def save(self, ctx_data):
        """Saves snapshot reference file to disk."""
        # Make sure directory exists before saving to file
        try:
            os.makedirs(os.path.dirname(self.filepath))
        except OSError:
            pass

        # use binary mode not to convert \n to OS-specific newlines;
        with open(self.filepath, 'wb') as outfile:
            outfile.write(ctx_data)

    def assert_matches(self, ctx_data):
        """Asserts whether `ctx_data` matches the reference snapshot.

        The `ctx` data will be cleaned prior to being stored or compared
        against any references.

        Implementation detail: the reason why this function asserts and
        doesn't return a boolean is to have useful diffs upon assertion
        failures.
        It would be possible to implement custom pytest assertion classes
        but that's beyond the simplest implementation :)
        """
        ctx_data = self.serialize(ctx_data)

        if self.generate:
            self.save(ctx_data)
            return

        if self.reference is None:
            raise AssertionError(
                'Snapshot file "%s" does not exist.' % self.filepath
            )

        assert self.reference == ctx_data


class SnapshotStack(object):
    """Context processor implementing a simple stack of `Snapshot`s.

    >> s = SnapshotStack('/foo/bar/')
    >> with s.push('foo'):
    >>    # context is 'foo'
    >>    with s.push('bar'):
    >>        # context is 'foo.bar'

    Pushing a list of values will be flattened to individual values when
    determining the context:

    >> with s.push(['foo', 'bar']):
    >>    # context is 'foo.bar'
    """

    def __init__(self, snapshot_kwargs):
        self.stack = []
        self.snapshot_kwargs = snapshot_kwargs

    def __enter__(self):
        return Snapshot(self.ctx_name, **self.snapshot_kwargs)

    def __exit__(self, *args, **kwargs):
        self.pop()

    @property
    def ctx_name(self):
        # Disallow leading forward slashes
        stack_items = filter(None, [
            item.replace('/', '', 1) if item.startswith('/') else item
            for item in flatten(self.stack)
        ])
        return ''.join([
            '%s%s' % (
                '' if i == 0 or i != 0 and stack_items[i-1].endswith('/') else '.',
                item
            )
            for i, item in enumerate(stack_items)
        ])

    def push(self, value):
        self.stack.append(value)
        return self

    def pop(self):
        self.stack.pop()
        return self
