# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django.utils.lru_cache import lru_cache

from pootle.core.browser import ItemTypes
from pootle.core.decorators import get_path_obj, permission_required
from pootle.core.helpers import get_sidebar_announcements_context
from pootle.core.views import (PootleBrowseView, PootleExportView,
                               PootleTranslateView)
from pootle_app.models import Directory
from pootle_app.views.admin.permissions import admin_permissions
from pootle_store.models import Store

from .models import Project, ProjectResource, ProjectSet


class ProjectMixin(object):
    model = Project
    browse_url_path = "pootle-project-browse"
    export_url_path = "pootle-project-export"
    translate_url_path = "pootle-project-translate"
    template_extends = 'projects/base.html'

    @property
    def ctx_path(self):
        return "/projects/%s/" % self.project.code

    @property
    def permission_context(self):
        return self.project.directory

    @cached_property
    def project(self):
        project = get_object_or_404(
            Project.objects.select_related("directory"),
            code=self.kwargs["project_code"])
        if project.disabled and not self.request.user.is_superuser:
            raise Http404
        return project

    @property
    def url_kwargs(self):
        return {
            "project_code": self.project.code,
            "dir_path": self.kwargs["dir_path"],
            "filename": self.kwargs["filename"]}

    @lru_cache()
    def get_object(self):
        if not (self.kwargs["dir_path"] or self.kwargs["filename"]):
            return self.project

        project_path = (
            "/%s/%s%s"
            % (self.project.code,
               self.kwargs['dir_path'],
               self.kwargs['filename']))
        regex = r"^/[^/]*%s$" % project_path
        if not self.kwargs["filename"]:
            dirs = Directory.objects.live()
            if self.kwargs['dir_path'].count("/"):
                tp_prefix = "parent__" * self.kwargs['dir_path'].count("/")
                dirs = dirs.select_related(
                    "%stranslationproject" % tp_prefix,
                    "%stranslationproject__language" % tp_prefix)
            resources = dirs.filter(
                pootle_path__endswith=project_path,
                pootle_path__regex=regex,
            )
        else:
            resources = (
                Store.objects.live()
                             .select_related("translation_project__language")
                             .filter(translation_project__project=self.project)
                             .filter(pootle_path__endswith=project_path)
                             .filter(pootle_path__regex=regex))
        if resources:
            return ProjectResource(
                resources,
                ("/projects/%(project_code)s/%(dir_path)s%(filename)s"
                 % self.kwargs))
        raise Http404

    @property
    def resource_path(self):
        return "%(dir_path)s%(filename)s" % self.kwargs


class ProjectBrowseView(ProjectMixin, PootleBrowseView):

    @property
    def stats(self):
        return self.object.get_stats_for_user(self.request.user)

    @cached_property
    def items(self):
        return self.object.get_children_for_user(self.request.user)

    @property
    def pootle_path(self):
        return self.object.pootle_path

    @property
    def permission_context(self):
        return self.project.directory

    @cached_property
    def sidebar_announcements(self):
        return get_sidebar_announcements_context(
            self.request,
            (self.project, ))

    @property
    def url_kwargs(self):
        return self.kwargs

    def get_item_type(self, path_obj):
        return ItemTypes.LANGUAGE

    def get_item_title(self, path_obj):
        if self.kwargs['dir_path'] or self.kwargs['filename']:
            return path_obj.translation_project.language.name
        return path_obj.language.name


class ProjectTranslateView(ProjectMixin, PootleTranslateView):
    required_permission = "administrate"

    @property
    def pootle_path(self):
        return self.object.pootle_path


class ProjectExportView(ProjectMixin, PootleExportView):
    source_language = "en"


@get_path_obj
@permission_required('administrate')
def project_admin_permissions(request, project):
    ctx = {
        'page': 'admin-permissions',

        'browse_url': reverse('pootle-project-browse', kwargs={
            'project_code': project.code,
            'dir_path': '',
            'filename': '',
        }),
        'translate_url': reverse('pootle-project-translate', kwargs={
            'project_code': project.code,
            'dir_path': '',
            'filename': '',
        }),

        'project': project,
        'directory': project.directory,
    }

    return admin_permissions(request, project.directory,
                             'projects/admin/permissions.html', ctx)


class ProjectsMixin(object):
    template_extends = 'projects/all/base.html'
    browse_url_path = "pootle-projects-browse"
    export_url_path = "pootle-projects-export"
    translate_url_path = "pootle-projects-translate"

    @lru_cache()
    def get_object(self):
        user_projects = (
            Project.objects.for_user(self.request.user)
                           .select_related("directory__pootle_path"))
        return ProjectSet(user_projects)

    @property
    def permission_context(self):
        return self.get_object().directory

    @property
    def has_admin_access(self):
        return self.request.user.is_superuser

    @property
    def url_kwargs(self):
        return {}


class ProjectsBrowseView(ProjectsMixin, PootleBrowseView):

    @property
    def sidebar_announcements(self):
        return {}, None

    def get(self, *args, **kwargs):
        response = super(ProjectsBrowseView, self).get(*args, **kwargs)
        response.set_cookie('pootle-language', "projects")
        return response

    def get_item_type(self, path_obj):
        return ItemTypes.PROJECT

    def get_item_title(self, path_obj):
        return path_obj.fullname


class ProjectsTranslateView(ProjectsMixin, PootleTranslateView):
    required_permission = "administrate"


class ProjectsExportView(ProjectsMixin, PootleExportView):
    source_language = "en"
