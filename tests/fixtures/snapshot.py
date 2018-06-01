# -*- coding: utf-8 -*-
#
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import pytest


@pytest.fixture
def snapshot_stack(data_dir, should_generate_snapshots):
    """Context processor providing a stack for snapshots."""
    from pootle.core.models.snapshot import SnapshotStack
    snapshot_kwargs = {
        'data_dir': data_dir('snapshots'),
        'generate': should_generate_snapshots,
    }
    return SnapshotStack(snapshot_kwargs)
