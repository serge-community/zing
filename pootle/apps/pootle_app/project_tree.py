# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import errno
import logging
import os

from django.conf import settings

from pootle.core.log import STORE_RESURRECTED, store_log
from pootle.core.utils.timezone import datetime_min
from pootle_app.models.directory import Directory
from pootle_store.models import Store
from pootle_store.util import relative_real_path


FILE_EXTENSIONS = ['po']


def get_matching_language_dirs(project_dir, language):
    return [lang_dir for lang_dir in os.listdir(project_dir)
            if language.code == lang_dir]


def get_or_make_language_dir(project_dir, language, make_dirs):
    matching_language_dirs = get_matching_language_dirs(project_dir, language)
    if len(matching_language_dirs) != 0:
        return os.path.join(project_dir, matching_language_dirs[0])

    if not make_dirs:
        raise IndexError('Directory not found for language %s, project %s' %
                         (language.code, project_dir))

    # If no matching directories can be found, create them
    language_dir = os.path.join(project_dir, language.code)
    os.mkdir(language_dir)
    return language_dir


def get_language_dir(project_dir, language, make_dirs):
    language_dir = os.path.join(project_dir, language.code)
    if not os.path.exists(language_dir):
        return get_or_make_language_dir(project_dir, language, make_dirs)
    return language_dir


def get_translation_project_dir(language, project_dir, make_dirs=False):
    """Returns the base directory containing translations files for the
    project.

    :param make_dirs: if ``True``, project and language directories will be
                      created as necessary.
    """
    return get_language_dir(project_dir, language, make_dirs)


def is_hidden_file(path):
    return path[0] == '.'


def split_files_and_dirs(real_dir):
    files = []
    dirs = []
    for child_path in os.listdir(real_dir):
        if is_hidden_file(child_path):
            continue
        full_child_path = os.path.join(real_dir, child_path)
        should_include_file = (
            os.path.isfile(full_child_path)
            and os.path.splitext(full_child_path)[1][1:] in FILE_EXTENSIONS
        )
        if should_include_file:
            files.append(child_path)
        elif os.path.isdir(full_child_path):
            dirs.append(child_path)
    return files, dirs


def add_items(fs_items_set, db_items, create_or_resurrect_db_item, parent):
    """Add/make obsolete the database items to correspond to the filesystem.

    :param fs_items_set: items (dirs, files) currently in the filesystem
    :param db_items: dict (name, item) of items (dirs, stores) currently in the
        database
    :create_or_resurrect_db_item: callable that will create a new db item
        or resurrect an obsolete db item with a given name and parent.
    :parent: parent db directory for the items
    :return: list of all items, list of newly added items
    :rtype: tuple
    """
    items = []
    new_items = []
    db_items_set = set(db_items)

    items_to_delete = db_items_set - fs_items_set
    items_to_create = fs_items_set - db_items_set

    for name in items_to_delete:
        db_items[name].makeobsolete()
    if len(items_to_delete) > 0:
        parent.update_all_cache()

    for name in db_items_set - items_to_delete:
        items.append(db_items[name])

    for name in items_to_create:
        item = create_or_resurrect_db_item(name)
        items.append(item)
        new_items.append(item)
        try:
            item.save()
        except Exception:
            logging.exception('Error while adding %s', item)

    return items, new_items


def create_or_resurrect_store(f, parent, name, translation_project):
    """Create or resurrect a store db item with given name and parent."""
    try:
        store = Store.objects.get(parent=parent, name=name)
        store.obsolete = False
        store.file_mtime = datetime_min
        if store.last_sync_revision is None:
            store.last_sync_revision = store.get_max_unit_revision()

        store_log(user='system', action=STORE_RESURRECTED,
                  path=store.pootle_path, store=store.id)
    except Store.DoesNotExist:
        store = Store.objects.create(
            file=f, parent=parent,
            name=name, translation_project=translation_project)
    store.mark_all_dirty()
    return store


def create_or_resurrect_dir(name, parent):
    """Create or resurrect a directory db item with given name and parent."""
    try:
        directory = Directory.objects.get(parent=parent, name=name)
        directory.obsolete = False
    except Directory.DoesNotExist:
        directory = Directory(name=name, parent=parent)

    directory.mark_all_dirty()
    return directory


# TODO: rename function or even rewrite it
def add_files(translation_project, relative_dir, db_dir):
    podir_path = to_podir_path(relative_dir)
    files, dirs = split_files_and_dirs(podir_path)
    file_set = set(files)
    dir_set = set(dirs)

    existing_stores = dict((store.name, store) for store in
                           db_dir.child_stores.live().exclude(file='')
                                                     .iterator())
    existing_dirs = dict((dir.name, dir) for dir in
                         db_dir.child_dirs.live().iterator())

    files, new_files = add_items(
        file_set,
        existing_stores,
        lambda name: create_or_resurrect_store(
            f=os.path.join(relative_dir, name),
            parent=db_dir,
            name=name,
            translation_project=translation_project,
        ),
        db_dir,
    )

    db_subdirs, new_db_subdirs_ = add_items(
        dir_set,
        existing_dirs,
        lambda name: create_or_resurrect_dir(name=name, parent=db_dir),
        db_dir,
    )

    is_empty = len(files) == 0
    for db_subdir in db_subdirs:
        fs_subdir = os.path.join(relative_dir, db_subdir.name)
        _files, _new_files, _is_empty = add_files(
            translation_project,
            fs_subdir,
            db_subdir,
        )
        files += _files
        new_files += _new_files
        is_empty &= _is_empty

    if is_empty:
        db_dir.makeobsolete()

    return files, new_files, is_empty


def to_podir_path(path):
    path = relative_real_path(path)
    return os.path.join(settings.ZING_TRANSLATION_DIRECTORY, path)


def translation_project_dir_exists(language, project):
    """Tests if there are translation files corresponding to the given
    :param:`language` and :param:`project`.
    """
    # find directory with the language name in the project dir
    try:
        dirpath_, dirnames, filename = os.walk(project.get_real_path()).next()
        if language.code in dirnames:
            return True
    except StopIteration:
        pass

    return False


def does_not_exist(path):
    if os.path.exists(path):
        return False

    try:
        os.stat(path)
        # what the hell?
    except OSError as e:
        if e.errno == errno.ENOENT:
            # explicit no such file or directory
            return True
