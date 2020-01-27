# -*- coding: utf-8 -*-
#
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from functools import lru_cache

from django.http import Http404

from pootle.core.url_helpers import split_pootle_path
from pootle.core.views.api import APIView
from pootle.forms import AddDueDateForm, EditDueDateForm
from pootle.models import DueDate
from pootle_app.models.permissions import check_user_permission
from pootle_language.models import Language
from pootle_project.models import Project
from pootle_translationproject.models import TranslationProject


class CanAdminPath(object):
    """Determines whether the request is allowed to continue based on path
    permissions.

    Views must indicate which field contains the path data via the
    `path_field = 'field_name'` attribute.
    """

    @lru_cache()
    def _get_ctx_obj(self, path, user):
        lang_code, proj_code = split_pootle_path(path)[:2]

        if proj_code and not lang_code:
            try:
                return Project.objects.select_related(
                    'directory'
                ).get(code=proj_code)
            except Project.DoesNotExist:
                return None

        if lang_code:
            if proj_code:
                try:
                    return TranslationProject.objects.get_for_user(
                        user=user,
                        language_code=lang_code,
                        project_code=proj_code,
                        select_related=['directory'],
                    )
                except TranslationProject.DoesNotExist:
                    return None

            try:
                return Language.objects.select_related(
                    'directory'
                ).get(code=lang_code)
            except Language.DoesNotExist:
                return None

        return None

    def _check_path_permission(self, path, user):
        ctx_obj = self._get_ctx_obj(path, user)
        if ctx_obj is None:
            raise Http404

        can_admin_path = check_user_permission(user, 'administrate',
                                               ctx_obj.directory)
        if not can_admin_path:
            return False

        return True

    def has_permission(self, request, view):
        if request.method != 'POST':
            return True

        path = view.request_data[view.path_field]
        return self._check_path_permission(path, request.user)

    def has_object_permission(self, request, view, obj):
        path = obj.pootle_path
        return self._check_path_permission(path, request.user)


class DueDateView(APIView):
    model = DueDate
    restrict_to_methods = ('POST', 'PUT', 'DELETE', )
    fields = ('id', 'due_on', 'modified_by', 'pootle_path', )
    add_form_class = AddDueDateForm
    edit_form_class = EditDueDateForm
    permission_classes = [CanAdminPath]
    path_field = 'pootle_path'

    def get_form_kwargs(self):
        kwargs = super(DueDateView, self).get_form_kwargs()
        kwargs['data'].update({
            'modified_by': self.request.user.id,
        })
        return kwargs
