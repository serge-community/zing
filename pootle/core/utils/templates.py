# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
#
# This file is a part of the Pootle project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from django.core.exceptions import SuspiciousFileOperation
from django.template import TemplateDoesNotExist
from django.template.engine import Engine
from django.utils._os import safe_join


def get_template_source(name, dirs=None):
    """Retrieves the template's source contents.

    :param name: Template's filename, as passed to the template loader.
    :param dirs: list of directories to optionally override the defaults.
    :return: tuple including file contents and file path.
    """
    loaders = []
    for loader in Engine.get_default().template_loaders:
        # The cached loader includes the actual loaders underneath
        if hasattr(loader, 'loaders'):
            loaders.extend(loader.loaders)
        else:
            loaders.append(loader)

    for loader in loaders:
        for template_dir in loader.get_dirs():
            try:
                filename = safe_join(template_dir, name)
            except SuspiciousFileOperation:
                # The joined path was located outside of this template_dir
                # (it might be inside another one, so this isn't fatal).
                continue

            try:
                with open(filename, encoding=loader.engine.file_charset) as fp:
                    return fp.read()
            except FileNotFoundError:
                continue

    raise TemplateDoesNotExist(name)
