# -*- coding: utf-8 -*-
#
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from django.views.decorators.cache import never_cache
from django.views.generic import View

from pootle.core.http import JsonResponse, JsonResponseBadRequest
from pootle.forms.task import GetTaskForm
from pootle.models import DueDate


PENDING_TASKS_LIMIT = 5


class TaskView(View):
    http_method_names = ('get', )
    form_class = GetTaskForm

    @never_cache
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponseBadRequest({
                'msg': 'Not enough privileges',
            })

        form_data = self.request.GET.dict()
        form_data.update({
            'language': kwargs['language_code'],
        })
        form = self.form_class(form_data)
        if not form.is_valid():
            # FIXME: make raising a `ValidationError` return from parent
            # classes the appropriate response
            return JsonResponseBadRequest({
                'errors': form.errors,
            })

        context = self.get_context_data(form=form)
        return JsonResponse(context)

    def get_context_data(self, *args, **kwargs):
        form = kwargs.pop('form')
        lang_code = form.cleaned_data['language'].code
        offset = form.cleaned_data['offset']
        start = offset
        end = offset + PENDING_TASKS_LIMIT

        tasks = DueDate.tasks(lang_code, user=self.request.user)[start:end]
        return {
            'items': tasks,
        }
