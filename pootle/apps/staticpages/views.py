# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import render
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, TemplateView, UpdateView

from pootle.core.http import JsonResponse, JsonResponseBadRequest
from pootle.core.views.mixins import SuperuserRequiredMixin
from pootle_misc.util import ajax_required

from .forms import agreement_form_factory
from .models import AbstractPage, LegalPage, StaticPage


class PageModelMixin(object):
    """Mixin used to set the view's page model according to the
    `page_type` argument caught in a url pattern.
    """

    def dispatch(self, request, *args, **kwargs):
        self.page_type = kwargs.get("page_type", None)
        self.model = {"legal": LegalPage, "static": StaticPage}.get(self.page_type)

        if self.model is None:
            raise Http404

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({"page_display_name": self.model.display_name})
        return ctx

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"label_suffix": ""})
        return kwargs


class AdminCtxMixin(object):
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({"page": "admin-pages"})
        return ctx


class AdminTemplateView(SuperuserRequiredMixin, AdminCtxMixin, TemplateView):

    template_name = "admin/staticpages/page_list.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(
            {
                "legalpages": LegalPage.objects.all(),
                "staticpages": StaticPage.objects.all(),
            }
        )
        return ctx


class PageCreateView(SuperuserRequiredMixin, AdminCtxMixin, PageModelMixin, CreateView):
    fields = ("title", "virtual_path", "active", "body")

    success_url = reverse_lazy("pootle-staticpages")
    template_name = "admin/staticpages/page_create.html"

    def get_initial(self):
        initial = super().get_initial()

        next_page_number = AbstractPage.max_pk() + 1
        initial_args = {
            "title": _("Page Title"),
            "virtual_path": "page-%d" % next_page_number,
        }

        initial.update(initial_args)

        return initial


class PageUpdateView(SuperuserRequiredMixin, AdminCtxMixin, PageModelMixin, UpdateView):
    fields = ("title", "virtual_path", "active", "body")

    success_url = reverse_lazy("pootle-staticpages")
    template_name = "admin/staticpages/page_update.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({"show_delete": True, "page_type": self.page_type})
        return ctx


class PageDeleteView(SuperuserRequiredMixin, PageModelMixin, DeleteView):

    success_url = reverse_lazy("pootle-staticpages")


def display_page(request, virtual_path):
    """Displays an active page defined in `virtual_path`."""
    page = None
    for page_model in AbstractPage.__subclasses__():
        try:
            page = page_model.objects.live(request.user).get(virtual_path=virtual_path,)
        except ObjectDoesNotExist:
            pass

    if page is None:
        raise Http404

    template_name = "staticpages/page_display.html"
    if request.is_ajax():
        template_name = "staticpages/_body.html"

    ctx = {
        "page": page,
    }
    return render(request, template_name, ctx)


def _get_rendered_agreement(request, form):
    template = get_template("staticpages/agreement.html")
    return template.render(context={"form": form}, request=request)


@ajax_required
def legal_agreement(request):
    """Displays the pending documents to be agreed by the current user."""
    pending_pages = LegalPage.objects.pending_user_agreement(request.user)
    form_class = agreement_form_factory(pending_pages, request.user)

    if request.method == "POST":
        form = form_class(request.POST)

        if form.is_valid():
            form.save()
            return JsonResponse({})

        rendered_form = _get_rendered_agreement(request, form)
        return JsonResponseBadRequest({"form": rendered_form})

    rendered_form = _get_rendered_agreement(request, form_class())
    return JsonResponse({"form": rendered_form})
