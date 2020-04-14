# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from django.forms import ValidationError
from django.http import Http404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.views.decorators.cache import never_cache
from django.views.generic import DetailView, View

from pootle.core.forms import PathForm
from pootle.core.url_helpers import get_path_parts, split_pootle_path
from pootle_app.models.permissions import check_permission
from pootle_misc.util import ajax_required

from .decorators import requires_permission, set_permissions
from .mixins import PootleJSONMixin


class PootleDetailView(DetailView):
    translate_url_path = ""
    browse_url_path = ""
    export_url_path = ""
    resource_path = ""

    @property
    def browse_url(self):
        return reverse(self.browse_url_path, kwargs=self.url_kwargs)

    @property
    def export_url(self):
        return reverse(self.export_url_path, kwargs=self.url_kwargs)

    @cached_property
    def has_admin_access(self):
        return check_permission("administrate", self.request)

    @property
    def language(self):
        if self.tp:
            return self.tp.language

    @property
    def permission_context(self):
        return self.get_object()

    @property
    def pootle_path(self):
        return self.object.pootle_path

    @property
    def project(self):
        if self.tp:
            return self.tp.project

    @property
    def tp(self):
        return None

    @property
    def translate_url(self):
        return reverse(self.translate_url_path, kwargs=self.url_kwargs)

    @set_permissions
    @requires_permission("view")
    def dispatch(self, request, *args, **kwargs):
        # get funky with the request 8/
        return super(PootleDetailView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        return {
            "object": self.object,
            "pootle_path": self.pootle_path,
            "project": self.project,
            "language": self.language,
            "translation_project": self.tp,
            "has_admin_access": self.has_admin_access,
            "resource_path": self.resource_path,
            "resource_path_parts": get_path_parts(self.resource_path),
            "translate_url": self.translate_url,
            "export_url": self.export_url,
            "browse_url": self.browse_url,
        }


class PootleJSON(PootleJSONMixin, PootleDetailView):
    @never_cache
    @method_decorator(ajax_required)
    @set_permissions
    @requires_permission("view")
    def dispatch(self, request, *args, **kwargs):
        return super(PootleJSON, self).dispatch(request, *args, **kwargs)


class PootleAdminView(DetailView):
    @set_permissions
    @requires_permission("administrate")
    def dispatch(self, request, *args, **kwargs):
        return super(PootleAdminView, self).dispatch(request, *args, **kwargs)

    @property
    def permission_context(self):
        return self.get_object().directory

    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)


class BasePathDispatcherView(View):
    form_class = PathForm

    language_view_class = None
    store_view_class = None
    directory_view_class = None
    projects_view_class = None
    project_view_class = None

    @never_cache
    def dispatch(self, request, *args, **kwargs):
        form = self.get_form()
        if not form.is_valid():
            raise Http404(ValidationError(form.errors))

        path = form.cleaned_data["path"]
        lang_code, proj_code, dir_path, filename = split_pootle_path(path)

        kwargs.update(
            {
                "language_code": lang_code,
                "project_code": proj_code,
                "dir_path": dir_path,
                "filename": filename,
            }
        )
        kwargs.update(**form.cleaned_data)

        view_class = self.get_view_class(lang_code, proj_code, dir_path, filename)
        return view_class.as_view()(request, *args, **kwargs)

    def get_form(self):
        return self.form_class(self.request.GET)

    def get_view_class(self, lang_code, proj_code, dir_path, filename):
        if lang_code and proj_code:
            # /<lang>/<proj>/[<dir>/]<filename>.ext
            if filename:
                return self.store_view_class
            # /<lang>/<proj>/[<dir>/]
            return self.directory_view_class

        # /<lang>/
        if lang_code:
            return self.language_view_class

        # /projects/<proj>/
        if proj_code:
            return self.project_view_class

        # /projects/[<proj>/[<dir>/]<filename>.ext]
        return self.projects_view_class
