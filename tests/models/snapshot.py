# -*- coding: utf-8 -*-
#
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import pytest

from django.template import Context, RequestContext
from django.test.utils import ContextList

from pootle.core.models.snapshot import Snapshot, SnapshotStack


@pytest.mark.parametrize('bogus_filepath', [
    '../test',
    '../../test',
    '../foo/../bar/../test',
])
def test_snapshot_filepath_out_of_data_dir(tmpdir, bogus_filepath):
    """Tests files cannot fall anywhere but under `data_dir`."""
    reference_file = tmpdir.join('non-existant')
    snapshot = Snapshot(bogus_filepath, data_dir=reference_file.dirname)
    with pytest.raises(ValueError):
        snapshot.filepath


def test_snapshot_filepath(tmpdir):
    """Tests file paths fall under `data_dir`."""
    reference_file = tmpdir.join('foo')
    snapshot = Snapshot('foo', data_dir=reference_file.dirname)
    snapshot.filepath == reference_file


def test_snapshot_reference_non_existant():
    """Tests snapshots for non-existant references."""
    snapshot = Snapshot('bogus')
    assert snapshot.reference is None


def test_snapshot_reference(tmpdir):
    """Tests snapshot references are loaded."""
    reference_file = tmpdir.join('test.json')
    snapshot = Snapshot('test', data_dir=reference_file.dirname)
    reference_content = 'FOO'
    reference_file.write(reference_content)
    assert snapshot.reference == reference_content


@pytest.mark.parametrize('input, clean_output', [
    (None, None),
    ([], []),

    ({'foo': 'bar'}, {'foo': 'bar'}),
    ({'block': True, 'forloop': False, 'lastupdated': 1234}, {}),

    ([{'foo': 'bar'}], [{'foo': 'bar'}]),
    ([{'block': True}, {'forloop': False, 'lastupdated': 1234}], [{}, {}]),

    (ContextList([Context({'foo': 'bar'})]), {'foo': 'bar'}),
    (ContextList([Context({'block': True})]), {}),
    (ContextList([Context({'block': True}), Context({'foo': 'bar'})]),
     {'foo': 'bar'}),

    (RequestContext(None, {'foo': 'bar'}), {'foo': 'bar'}),
])
def test_snapshot_clean(input, clean_output):
    """Tests the cleanup of snapshot contexts."""
    snapshot = Snapshot('test')
    assert snapshot.clean(input) == clean_output


def test_snapshot_assert_matches_generate(tmpdir):
    """Tests the snapshot is generated if instructed to do so."""
    reference_file = tmpdir.join('test.json')
    snapshot = Snapshot('test', data_dir=reference_file.dirname, generate=True)
    assert snapshot.reference is None
    # The assertion function reported nothing
    assert snapshot.assert_matches({}) is None
    # But the reference file should now be created
    assert reference_file.exists()


def test_snapshot_assert_matches_generate_subdirs(tmpdir):
    """Tests the snapshot is generated also with subdirectories."""
    reference_file = tmpdir.join('non-existant')
    snapshot = Snapshot('subdir/test', data_dir=reference_file.dirname,
                        generate=True)
    assert snapshot.reference is None
    # The assertion function reported nothing
    assert snapshot.assert_matches({}) is None
    # But the reference dir + file should now be created
    assert reference_file.join('../subdir/test.json').exists()


def test_snapshot_assert_matches_generate_subdirs_existing(tmpdir):
    """Tests the snapshot is generated also with existing subdirectories."""
    reference_file = tmpdir.join('subdir')
    snapshot = Snapshot('subdir/test', data_dir=reference_file.dirname,
                        generate=True)
    assert snapshot.reference is None
    # The assertion function reported nothing
    assert snapshot.assert_matches({}) is None
    # But the reference dir + file should now be created
    assert reference_file.join('test.json').exists()


def test_snapshot_assert_matches_error(tmpdir):
    """Tests assertion errors out if the reference does not exist."""
    reference_file = tmpdir.join('test.json')
    snapshot = Snapshot('test', data_dir=reference_file.dirname)
    assert snapshot.reference is None
    with pytest.raises(AssertionError):
        snapshot.assert_matches({'foo': 'bar'})


def test_snapshot_assert_matches(tmpdir):
    """Tests assertion matching."""
    reference_file = tmpdir.join('test.json')
    snapshot = Snapshot('test', data_dir=reference_file.dirname)
    reference_content = 'FOO'
    reference_file.write(snapshot.serialize(reference_content))
    snapshot.assert_matches(reference_content)


@pytest.mark.parametrize('stack_values, expected_ctx_name', [
    ('', ''),
    ('/', ''),
    (['/'], ''),

    (['/', 'foo'], 'foo'),
    (['/', 'foo', '/'], 'foo'),
    (['/', 'foo', ''], 'foo'),

    (['/foo', 'bar'], 'foo.bar'),
    (['foo', '/bar'], 'foo.bar'),
    (['foo', '/', 'bar'], 'foo.bar'),

    (['foo/', 'bar'], 'foo/bar'),
    (['foo/', 'bar/', 'baz'], 'foo/bar/baz'),
    (['foo/', 'bar/', '/baz'], 'foo/bar/baz'),
    (['foo/bar/baz'], 'foo/bar/baz'),
    ('foo/bar/baz', 'foo/bar/baz'),

    (['foo', 'bar/'], 'foo.bar/'),
    (['foo/bar/baz', 'blah'], 'foo/bar/baz.blah'),
])
def test_snapshot_stack_ctx_name(stack_values, expected_ctx_name):
    """Tests SnapshotStack's context name generation."""
    stack = SnapshotStack({})
    stack.push(stack_values)
    assert stack.ctx_name == expected_ctx_name
