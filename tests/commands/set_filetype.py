# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
#
# This file is a part of the Pootle project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import pytest

from django.core.management import call_command
from django.core.management.base import CommandError

from pootle_project.models import Project


@pytest.mark.cmd
@pytest.mark.django_db
def test_cmd_set_project_filetype(dummy_project_filetypes,
                                  tp0, po, po2):
    project = tp0.project
    tps = project.translationproject_set.all()
    result = project.filetype_tool.result

    project.filetype_tool.add_filetype(po2)
    call_command("set_filetype", "--project=project0", "special_po_2")

    for i, tp in enumerate(tps):
        assert result[i] == (tp, po2, None, None)

    # test getting from_filetype
    result.clear()
    call_command(
        "set_filetype",
        "--project=project0",
        "--from-filetype=po",
        "special_po_2")
    for i, tp in enumerate(tps):
        assert result[i] == (tp, po2, po, None)

    # test getting match
    result.clear()
    call_command(
        "set_filetype",
        "--project=project0",
        "--matching=bar",
        "special_po_2")
    for i, tp in enumerate(tps):
        assert result[i] == (tp, po2, None, "bar")

    # test getting both
    result.clear()
    call_command(
        "set_filetype",
        "--project=project0",
        "--from-filetype=po",
        "--matching=bar",
        "special_po_2")
    for i, tp in enumerate(tps):
        assert result[i] == (tp, po2, po, "bar")


@pytest.mark.cmd
@pytest.mark.django_db
def test_cmd_set_all_project_filetypes(dummy_project_filetypes, po2):

    for project in Project.objects.all():
        project.filetype_tool.add_filetype(po2)

    # grab the result object from a project
    result = project.filetype_tool.result

    call_command("set_filetype", "special_po_2")
    i = 0
    for project in Project.objects.all():
        project_tps = project.translationproject_set.all()
        for tp in project_tps:
            assert result[i] == (tp, po2, None, None)
            i += 1


@pytest.mark.cmd
@pytest.mark.django_db
def test_cmd_set_project_filetypes_bad():
    with pytest.raises(CommandError):
        call_command(
            "set_filetype",
            "--project=project0",
            "--from-filetype=FORMAT_DOES_NOT_EXIST",
            "po")
    with pytest.raises(CommandError):
        call_command(
            "set_filetype",
            "--project=project0",
            "FORMAT_DOES_NOT_EXIST")
    with pytest.raises(CommandError):
        call_command(
            "set_filetype",
            "--project=PROJECT_DOES_NOT_EXIST",
            "po")
