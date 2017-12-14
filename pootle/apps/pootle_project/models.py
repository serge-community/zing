# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import logging
import os
from collections import OrderedDict

from translate.filters import checks

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.encoding import iri_to_uri
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from pootle.core.cache import make_method_key
from pootle.core.mixins import CachedTreeItem
from pootle.core.models import VirtualResource
from pootle.core.url_helpers import (get_editor_filter, get_path_sortkey,
                                     split_pootle_path, to_tp_relative_path)
from pootle.core.utils.decorators import disable_for_loaddata
from pootle_app.models.directory import Directory
from pootle_app.models.permissions import PermissionSet
from pootle_store.models import Store
from pootle_store.util import absolute_real_path


RESERVED_PROJECT_CODES = ('admin', 'translate', 'settings')
PROJECT_CHECKERS = {
    "standard": checks.StandardChecker,
    "openoffice": checks.OpenOfficeChecker,
    "libreoffice": checks.LibreOfficeChecker,
    "mozilla": checks.MozillaChecker,
    "kde": checks.KdeChecker,
    "wx": checks.KdeChecker,
    "gnome": checks.GnomeChecker,
    "creativecommons": checks.CCLicenseChecker,
    "drupal": checks.DrupalChecker,
    "terminology": checks.TermChecker,
}


class ProjectManager(models.Manager):

    def cached_dict(self, user):
        """Return a cached ordered dictionary of projects tuples for `user`.

        - Admins always get all projects.
        - Regular users only get enabled projects accessible to them.

        :param user: The user for whom projects need to be retrieved for.
        :return: An ordered dictionary of project tuples including
          (`fullname`, `disabled`) and `code` is a key in the dictionary.
        """
        if not user.is_superuser:
            cache_params = {'username': user.username}
        else:
            cache_params = {'is_admin': user.is_superuser}
        cache_key = make_method_key('Project', 'cached_dict', cache_params)
        projects = cache.get(cache_key)
        if not projects:
            logging.debug('Cache miss for %s', cache_key)
            projects_dict = self.for_user(user).order_by('fullname') \
                                               .values('code', 'fullname',
                                                       'disabled')

            projects = OrderedDict(
                (project.pop('code'), project) for project in projects_dict
            )
            cache.set(cache_key, projects, settings.POOTLE_CACHE_TIMEOUT)

        return projects

    def enabled(self):
        return self.filter(disabled=False)

    def get_for_user(self, project_code, user):
        """Gets a `project_code` project for a specific `user`.

        - Admins can get the project even if it's disabled.
        - Regular users only get a project if it's not disabled and
            it is accessible to them.

        :param project_code: The code of the project to retrieve.
        :param user: The user for whom the project needs to be retrieved.
        :return: The `Project` matching the params, raises otherwise.
        """
        if user.is_superuser:
            return self.get(code=project_code)

        return self.for_user(user).get(code=project_code)

    def for_user(self, user):
        """Filters projects for a specific user.

        - Admins always get all projects.
        - Regular users only get enabled projects accessible to them.

        :param user: The user for whom the projects need to be retrieved for.
        :return: A filtered queryset with `Project`s for `user`.
        """
        if user.is_superuser:
            return self.all()

        return self.enabled().filter(code__in=Project.accessible_by_user(user))


class ProjectURLMixin(object):
    """Mixin class providing URL methods to be shared across
    project-related classes.
    """

    def get_absolute_url(self):
        proj_code = split_pootle_path(self.pootle_path)[1]

        if proj_code is not None:
            pattern_name = 'pootle-project-browse'
            pattern_args = [proj_code, '']
        else:
            pattern_name = 'pootle-projects-browse'
            pattern_args = []

        return reverse(pattern_name, args=pattern_args)

    def get_translate_url(self, **kwargs):
        proj_code, dir_path, filename = split_pootle_path(self.pootle_path)[1:]

        if proj_code is not None:
            pattern_name = 'pootle-project-translate'
            pattern_args = [proj_code, dir_path, filename]
        else:
            pattern_name = 'pootle-projects-translate'
            pattern_args = []

        return u''.join([
            reverse(pattern_name, args=pattern_args),
            get_editor_filter(**kwargs),
        ])


def validate_not_reserved(value):
    if value in RESERVED_PROJECT_CODES:
        raise ValidationError(
            _('"%(code)s" cannot be used as a project code'),
            params={'code': value},
        )


class Project(models.Model, CachedTreeItem, ProjectURLMixin):

    code_help_text = _('A short code for the project. This should only '
                       'contain ASCII characters, numbers, and the underscore '
                       '(_) character.')
    # any changes to the `code` field may require updating the schema
    # see migration 0003_case_sensitive_schema.py
    code = models.CharField(max_length=255, null=False, unique=True,
                            db_index=True, verbose_name=_('Code'), blank=False,
                            validators=[validate_not_reserved],
                            help_text=code_help_text)

    fullname = models.CharField(max_length=255, null=False, blank=False,
                                verbose_name=_("Full Name"))

    checker_choices = [
        (checker, checker)
        for checker
        in sorted(PROJECT_CHECKERS.keys())]
    checkstyle = models.CharField(
        max_length=50,
        default='standard',
        null=False,
        choices=checker_choices,
        verbose_name=_('Quality Checks'))

    source_language = models.ForeignKey(
        'pootle_language.Language', db_index=True,
        verbose_name=_('Source Language'))

    directory = models.OneToOneField('pootle_app.Directory', db_index=True,
                                     editable=False)
    report_email = models.EmailField(
        max_length=254, blank=True, verbose_name=_("Errors Report Email"),
        help_text=_('An email address where issues with the source text '
                    'can be reported.'))

    screenshot_search_prefix = models.URLField(
        blank=True, null=True, verbose_name=_('Screenshot Search Prefix'))

    creation_time = models.DateTimeField(auto_now_add=True, db_index=True,
                                         editable=False, null=True)

    disabled = models.BooleanField(verbose_name=_('Disabled'), default=False)

    objects = ProjectManager()

    class Meta(object):
        ordering = ['code']
        db_table = 'pootle_app_project'

    @classmethod
    def accessible_by_user(cls, user):
        """Returns a list of project codes accessible by `user`.

        Checks for explicit `view` permissions for `user`, and extends
        them with the `default` (if logged-in) and `nobody` users' `view`
        permissions.

        Negative `hide` permissions are also taken into account and
        they'll forbid project access as far as there's no `view`
        permission set at the same level for the same user.

        :param user: The ``User`` instance to get accessible projects for.
        """
        if user.is_superuser:
            key = iri_to_uri('projects:all')
        else:
            username = user.username
            key = iri_to_uri('projects:accessible:%s' % username)
        user_projects = cache.get(key, None)

        if user_projects is not None:
            return user_projects

        logging.debug(u'Cache miss for %s', key)

        # FIXME: use `cls.objects.cached_dict().keys()`
        ALL_PROJECTS = cls.objects.values_list('code', flat=True)

        if user.is_superuser:
            user_projects = ALL_PROJECTS
        else:
            ALL_PROJECTS = set(ALL_PROJECTS)

            if user.is_anonymous:
                allow_usernames = [username]
                forbid_usernames = [username, 'default']
            else:
                allow_usernames = list(set([username, 'default', 'nobody']))
                forbid_usernames = list(set([username, 'default']))

            # Check root for `view` permissions

            root_permissions = PermissionSet.objects.filter(
                directory__pootle_path='/',
                user__username__in=allow_usernames,
                positive_permissions__codename='view',
            )
            if root_permissions.count():
                user_projects = ALL_PROJECTS
            else:
                user_projects = set()

            # Check specific permissions at the project level

            accessible_projects = cls.objects.filter(
                directory__permission_sets__positive_permissions__codename='view',
                directory__permission_sets__user__username__in=allow_usernames,
            ).values_list('code', flat=True)

            forbidden_projects = cls.objects.filter(
                directory__permission_sets__negative_permissions__codename='hide',
                directory__permission_sets__user__username__in=forbid_usernames,
            ).values_list('code', flat=True)

            allow_projects = set(accessible_projects)
            forbid_projects = set(forbidden_projects) - allow_projects
            user_projects = (user_projects.union(
                allow_projects)).difference(forbid_projects)

        user_projects = list(user_projects)
        cache.set(key, user_projects, settings.POOTLE_CACHE_TIMEOUT)

        return user_projects

    # # # # # # # # # # # # # #  Properties # # # # # # # # # # # # # # # # # #

    @property
    def name(self):
        return self.fullname

    @property
    def pootle_path(self):
        return "/projects/" + self.code + "/"

    @property
    def is_terminology(self):
        """Returns ``True`` if this project is a terminology project."""
        return self.checkstyle == 'terminology'

    @cached_property
    def languages(self):
        """Returns a list of active :cls:`~pootle_languages.models.Language`
        objects for this :cls:`~pootle_project.models.Project`.
        """
        from pootle_language.models import Language
        # FIXME: we should better have a way to automatically cache models with
        # built-in invalidation -- did I hear django-cache-machine?
        return Language.objects.filter(translationproject__project=self)

    @cached_property
    def resources(self):
        """Returns a list of :cls:`~pootle_app.models.Directory` and
        :cls:`~pootle_store.models.Store` resource paths available for
        this :cls:`~pootle_project.models.Project` across all languages.
        """
        cache_key = make_method_key(self, 'resources', self.code)
        resources = cache.get(cache_key, None)
        if resources is not None:
            return resources

        stores = Store.objects.live().order_by().filter(
            translation_project__project__pk=self.pk)
        dirs = Directory.objects.live().order_by().filter(
            pootle_path__regex=r"^/[^/]*/%s/" % self.code)
        resources = sorted(
            {to_tp_relative_path(pootle_path)
             for pootle_path
             in (set(stores.values_list("pootle_path", flat=True))
                 | set(dirs.values_list("pootle_path", flat=True)))},
            key=get_path_sortkey)
        cache.set(cache_key, resources, settings.POOTLE_CACHE_TIMEOUT)
        return resources

    # # # # # # # # # # # # # #  Methods # # # # # # # # # # # # # # # # # # #

    def __unicode__(self):
        return self.fullname

    def save(self, *args, **kwargs):
        self.fullname = self.fullname.strip()
        self.code = self.code.strip()

        # Force validation of fields.
        self.full_clean()

        requires_translation_directory = (
            not self.disabled
            and not self.directory_exists_on_disk()
        )
        if requires_translation_directory:
            os.makedirs(self.get_real_path())

        self.directory = Directory.objects.projects \
                                          .get_or_make_subdir(self.code)

        super(Project, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        directory = self.directory

        # Just doing a plain delete will collect all related objects in memory
        # before deleting: translation projects, stores, units, quality checks,
        # suggestions, and submissions.
        # This can easily take down a process. If we do a translation project
        # at a time and force garbage collection, things stay much more
        # managable.
        import gc
        gc.collect()
        for tp in self.translationproject_set.iterator():
            tp.delete()
            gc.collect()

        super(Project, self).delete(*args, **kwargs)

        directory.delete()

    def directory_exists_on_disk(self):
        """Checks if the actual directory for the project exists on disk."""
        return os.path.exists(self.get_real_path())

    # # # TreeItem

    def get_children(self):
        return self.translationproject_set.live()

    # # # /TreeItem

    def get_stats_for_user(self, user):
        self.set_children(self.get_children_for_user(user))

        return self.get_stats()

    def get_children_for_user(self, user, select_related=None):
        """Returns children translation projects for a specific `user`."""
        return (
            self.translationproject_set.for_user(user, select_related)
                                       .select_related("language"))

    def get_real_path(self):
        return absolute_real_path(self.code)

    def is_accessible_by(self, user):
        """Returns `True` if the current project is accessible by
        `user`.
        """
        if user.is_superuser:
            return True

        return self.code in Project.accessible_by_user(user)


class ProjectResource(VirtualResource, ProjectURLMixin):

    def __eq__(self, other):
        return (
            self.pootle_path == other.pootle_path
            and list(self.get_children()) == list(other.get_children()))

    def get_children_for_user(self, user, select_related=None):
        if select_related:
            return self.children.select_related(*select_related)
        return self.children

    def get_stats_for_user(self, user):
        return self.get_stats()


class ProjectSet(VirtualResource, ProjectURLMixin):

    def __eq__(self, other):
        return (
            self.pootle_path == other.pootle_path
            and list(self.get_children()) == list(other.get_children()))

    def __init__(self, resources, *args, **kwargs):
        self.directory = Directory.objects.projects
        super(ProjectSet, self).__init__(resources, self.directory.pootle_path)


@receiver([post_delete, post_save])
@disable_for_loaddata
def invalidate_resources_cache(**kwargs):
    instance = kwargs["instance"]
    if instance.__class__.__name__ not in ['Directory', 'Store']:
        return

    # Don't invalidate if the save didn't create new objects
    no_new_objects = (
        ('created' in kwargs
         and 'raw' in kwargs)
        and (not kwargs['created']
             or kwargs['raw']))

    if no_new_objects and instance.parent.get_children():
        return

    proj_code = split_pootle_path(instance.pootle_path)[1]
    if proj_code is not None:
        cache.delete(make_method_key(Project, 'resources', proj_code))


@receiver([post_delete, post_save])
def invalidate_accessible_projects_cache(**kwargs):
    instance = kwargs["instance"]
    # XXX: maybe use custom signals or simple function calls?
    if (instance.__class__.__name__ not in
        ['Project', 'TranslationProject', 'PermissionSet']):
        return

    cache.delete_pattern(make_method_key('Project', 'cached_dict', '*'))
    cache.delete('projects:all')
    cache.delete_pattern('projects:accessible:*')
