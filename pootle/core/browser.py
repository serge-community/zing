# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from django.utils.translation import ugettext_lazy as _


def make_generic_item(path_obj, **kwargs):
    """Template variables for each row in the table."""
    return {
        'href': path_obj.get_absolute_url(),
        'href_all': path_obj.get_translate_url(),
        'href_todo': path_obj.get_translate_url(state='incomplete', **kwargs),
        'href_sugg': path_obj.get_translate_url(state='suggestions', **kwargs),
        'href_critical': path_obj.get_critical_url(**kwargs),
        'title': path_obj.name,
        'code': path_obj.code,
        'is_disabled': getattr(path_obj, 'disabled', False),
    }


def make_directory_item(directory, **filters):
    item = make_generic_item(directory, **filters)
    item.update({
        'icon': 'folder',
    })
    return item


def make_store_item(store):
    item = make_generic_item(store)
    item.update({
        'icon': 'file',
    })
    return item


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


def make_project_item(translation_project):
    item = make_generic_item(translation_project)
    item.update({
        'icon': 'project',
        'title': translation_project.project.name,
    })
    return item


def make_language_item(translation_project):
    item = make_generic_item(translation_project)
    item.update({
        'icon': 'language',
        'title': translation_project.language.name,
    })
    return item


def make_xlanguage_item(resource_obj):
    translation_project = resource_obj.translation_project
    item = make_generic_item(resource_obj)
    item.update({
        'icon': 'language',
        'code': translation_project.language.code,
        'title': translation_project.language.name,
    })
    return item


def make_project_list_item(project):
    item = make_generic_item(project)
    item.update({
        'icon': 'project',
        'title': project.fullname,
    })
    return item
