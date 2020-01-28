# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from django.utils.translation import gettext_lazy as _


class ItemTypes(object):
    STORE = 0
    DIRECTORY = 1
    PROJECT = 2
    LANGUAGE = 3


def get_parent(path_obj):
    """Retrieves a representation of the parent object.

    :param path_obj: either a `Directory` or Store` instance.
    """
    parent_dir = path_obj.parent

    if parent_dir.is_project():
        return None

    if parent_dir.is_language():
        label = _('Back to language')
    else:
        label = _('Back to parent folder')

    return {
        'title': label,
        'href': parent_dir.get_absolute_url()
    }
