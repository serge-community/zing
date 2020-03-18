# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import copy
from functools import lru_cache

from translate.lang import data

from django import forms
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import Http404, QueryDict
from django.shortcuts import redirect
from django.template import loader
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext as _, to_locale
from django.utils.translation.trans_real import parse_accept_lang_header
from django.views.decorators.http import require_http_methods

from pootle.core.decorators import get_path_obj, get_resource, permission_required
from pootle.core.exceptions import Http400
from pootle.core.http import JsonResponse, JsonResponseBadRequest
from pootle.core.utils import dateformat
from pootle.core.views import BaseBrowseDataJSON, BasePathDispatcherView, PootleJSON
from pootle_app.models.directory import Directory
from pootle_app.models.permissions import check_permission, check_user_permission
from pootle_comment.forms import UnsecuredCommentForm
from pootle_language.views import LanguageBrowseView
from pootle_misc.checks import get_qc_data_by_name
from pootle_misc.util import ajax_required
from pootle_project.views import ProjectBrowseView, ProjectsBrowseView
from pootle_statistics.models import Submission, SubmissionFields, SubmissionTypes
from pootle_translationproject.views import TPBrowseStoreView, TPBrowseView

from .decorators import get_unit_context
from .forms import (
    UnitSearchForm,
    UnitViewRowsForm,
    unit_comment_form_factory,
    unit_form_factory,
)
from .models import Unit
from .unit.results import CtxRowResults, ViewRowResults
from .unit.search import DBSearchBackend
from .unit.timeline import Timeline
from .util import find_altsrcs


# The amount of TM results that will be provided
MAX_TM_RESULTS = 3


def get_alt_src_langs(request, user, translation_project):
    language = translation_project.language
    project = translation_project.project
    source_language = project.source_language

    langs = user.alt_src_langs.exclude(id__in=(language.id, source_language.id)).filter(
        translationproject__project=project
    )

    if not user.alt_src_langs.count():
        from pootle_language.models import Language

        accept = request.META.get("HTTP_ACCEPT_LANGUAGE", "")

        for accept_lang, __ in parse_accept_lang_header(accept):
            if accept_lang == "*":
                continue

            simplified = data.simplify_to_common(accept_lang)
            normalized = to_locale(data.normalize_code(simplified))
            code = to_locale(accept_lang)
            if normalized in (
                "en",
                "en_US",
                source_language.code,
                language.code,
            ) or code in ("en", "en_US", source_language.code, language.code):
                continue

            langs = Language.objects.filter(
                code__in=(normalized, code), translationproject__project=project,
            )
            if langs.count():
                break

    return langs


#
# Views used with XMLHttpRequest requests.
#


def _get_critical_checks_snippet(request, unit):
    """Retrieves the critical checks snippet.

    :param request: an `HttpRequest` object
    :param unit: a `Unit` instance for which critical checks need to be
        rendered.
    :return: rendered HTML snippet with the failing checks, or `None` if
        there are no critical failing checks.
    """
    if not unit.has_critical_checks():
        return None

    can_review = check_user_permission(request.user, "review", unit.store.parent)
    ctx = {
        "canreview": can_review,
        "unit": unit,
    }
    template = loader.get_template("editor/units/xhr_checks.html")
    return template.render(context=ctx, request=request)


@ajax_required
def get_uids(request):
    """Gets all uids based on search criteria

    :return: A JSON-encoded string containing the sorted list of unit IDs
        (uids)
    """
    search_form = UnitSearchForm(request.GET, user=request.user)

    if not search_form.is_valid():
        errors = search_form.errors.as_data()
        if "path" in errors:
            for error in errors["path"]:
                if error.code == "max_length":
                    raise Http400(_("Path too long."))
                elif error.code == "required":
                    raise Http400(_("Arguments missing."))
        raise Http404(forms.ValidationError(search_form.errors).messages)

    begin, end, total, uids = DBSearchBackend(
        request.user, **search_form.cleaned_data
    ).get_uids()

    last_store_id = None
    uid_groups = []
    group = []
    for uid, store_id in uids:
        if not store_id == last_store_id:
            if len(group) > 0:
                uid_groups.append(group)
                group = []
            last_store_id = store_id
        group.append(uid)

    if len(group) > 0:
        uid_groups.append(group)

    return JsonResponse(
        {"begin": begin, "end": end, "total": total, "uids": uid_groups}
    )


@ajax_required
def get_units(request):
    """Based on the vector of uids and the vector of header uids,
    return a dictionary of lightweight results for the view rows.

    :return: A JSON-encoded string containing the dictionary
    """
    form = UnitViewRowsForm(request.GET, user=request.user)

    if not form.is_valid():
        errors = form.errors.as_data()
        if "uids" in errors:
            for error in errors["uids"]:
                if error.code in ["invalid", "required"]:
                    raise Http400(error.message)
        raise Http404(forms.ValidationError(form.errors).messages)

    units = DBSearchBackend(request.user, **form.cleaned_data).get_units()

    return JsonResponse(ViewRowResults(units, form.cleaned_data["headers"]).data)


@ajax_required
@get_unit_context("view")
def get_context_units(request, unit):
    """Retrieves context units.

    :return: An object in JSON notation that contains the lightweight unit
        information for units around `unit`.
    """
    units_qs = request.store.units
    limit = 5

    units_before = []
    if unit.index > 0:
        limit_before = min(unit.index - 1, limit)
        units_before = units_qs.filter(index__gt=unit.index - 1 - limit).order_by(
            "index"
        )[:limit_before]

    # FIXME: can we avoid this query if length is known?
    units_after = units_qs.filter(index__gt=unit.index,)[:limit]

    return JsonResponse(
        {
            "before": CtxRowResults(units_before).data,
            "after": CtxRowResults(units_after).data,
        }
    )


@ajax_required
@require_http_methods(["POST", "DELETE"])
@get_unit_context("translate")
def comment(request, unit):
    """Dispatches the comment action according to the HTTP verb."""
    if request.method == "DELETE":
        return delete_comment(request, unit)
    elif request.method == "POST":
        return save_comment(request, unit)


def delete_comment(request, unit):
    """Deletes a comment by blanking its contents and records a new
    submission.
    """
    unit.commented_by = None
    unit.commented_on = None

    language = request.translation_project.language
    comment_form_class = unit_comment_form_factory(language)
    form = comment_form_class({}, instance=unit, request=request)

    if form.is_valid():
        form.save()
        return JsonResponse({})

    return JsonResponseBadRequest({"msg": _("Failed to remove comment.")})


def save_comment(request, unit):
    """Stores a new comment for the given ``unit``.

    :return: If the form validates, the cleaned comment is returned.
             An error message is returned otherwise.
    """
    # Update current unit instance's attributes
    unit.commented_by = request.user
    unit.commented_on = timezone.now().replace(microsecond=0)

    language = request.translation_project.language
    form = unit_comment_form_factory(language)(
        request.POST, instance=unit, request=request
    )

    if form.is_valid():
        form.save()

        user = request.user
        directory = unit.store.parent

        ctx = {
            "unit": unit,
            "language": language,
            "cantranslate": check_user_permission(user, "translate", directory),
            "cansuggest": check_user_permission(user, "suggest", directory),
        }
        t = loader.get_template("editor/units/xhr_comment.html")

        return JsonResponse({"comment": t.render(context=ctx, request=request)})

    return JsonResponseBadRequest({"msg": _("Comment submission failed.")})


class PootleUnitJSON(PootleJSON):
    model = Unit
    pk_url_kwarg = "uid"

    @cached_property
    def permission_context(self):
        self.object = self.get_object()
        tp_prefix = "parent__" * (self.pootle_path.count("/") - 3)
        return Directory.objects.select_related(
            "%stranslationproject__project" % tp_prefix
        ).get(pk=self.store.parent_id)

    @property
    def pootle_path(self):
        return self.store.pootle_path

    @cached_property
    def tp(self):
        return self.store.translation_project

    @cached_property
    def store(self):
        return self.object.store

    @cached_property
    def source_language(self):
        return self.project.source_language

    @cached_property
    def directory(self):
        return self.store.parent

    @lru_cache()
    def get_object(self):
        return super().get_object()


class UnitTimelineJSON(PootleUnitJSON):

    model = Unit
    pk_url_kwarg = "uid"

    template_name = "editor/units/xhr_timeline.html"

    @property
    def language(self):
        return self.object.store.translation_project.language

    @cached_property
    def permission_context(self):
        self.object = self.get_object()
        return self.project.directory

    @property
    def project(self):
        return self.object.store.translation_project.project

    @property
    def timeline(self):
        return Timeline(self.object)

    def get_context_data(self, *args, **kwargs):
        return dict(entries_group=self.timeline.grouped_entries, language=self.language)

    def get_queryset(self):
        return Unit.objects.get_translatable(self.request.user).select_related(
            "store__translation_project__language",
            "store__translation_project__project__directory",
        )

    def get_response_data(self, context):
        return {
            "uid": self.object.id,
            "entries_group": self.get_entries_group_data(context),
            "timeline": self.render_timeline(context),
        }

    def render_timeline(self, context):
        return loader.get_template(self.template_name).render(context=context)

    def get_entries_group_data(self, context):
        result = []
        for entry_group in context["entries_group"]:
            timestamp = None
            entry_datetime = entry_group["datetime"]
            if entry_datetime is not None:
                timestamp = (int(dateformat.format(entry_datetime, "U")),)
            result.append({"timestamp": timestamp})
        return result


class UnitEditJSON(PootleUnitJSON):
    def get_edit_template(self):
        return loader.get_template("editor/units/edit.html")

    def render_edit_template(self, context):
        return self.get_edit_template().render(context=context, request=self.request)

    def get_source_nplurals(self):
        if self.object.hasplural():
            return len(self.object.source.strings)
        return None

    def get_target_nplurals(self):
        source_nplurals = self.get_source_nplurals()
        return self.language.nplurals if source_nplurals is not None else 1

    def get_unit_values(self):
        target_nplurals = self.get_target_nplurals()
        unit_values = [value for value in self.object.target_f.strings]
        if len(unit_values) < target_nplurals:
            return unit_values + ((target_nplurals - len(unit_values)) * [""])
        return unit_values

    def get_unit_edit_form(self):
        form_class = unit_form_factory(
            self.language, self.get_source_nplurals(), self.request
        )
        return form_class(instance=self.object, request=self.request)

    def get_unit_comment_form(self):
        comment_form_class = unit_comment_form_factory(self.language)
        return comment_form_class({}, instance=self.object, request=self.request)

    @lru_cache()
    def get_alt_srcs(self):
        return find_altsrcs(
            self.object,
            get_alt_src_langs(self.request, self.request.user, self.tp),
            store=self.store,
            project=self.project,
        )

    def get_queryset(self):
        return Unit.objects.get_translatable(self.request.user).select_related(
            "store",
            "store__parent",
            "store__translation_project",
            "store__translation_project__project",
            "store__translation_project__project__source_language",
            "store__translation_project__language",
        )

    def get_sources(self):
        sources = {
            unit.language_code: unit.target.strings for unit in self.get_alt_srcs()
        }
        sources[self.source_language.code] = self.object.source_f.strings
        return sources

    def get_context_data(self, *args, **kwargs):
        return {
            "unit": self.object,
            "form": self.get_unit_edit_form(),
            "comment_form": self.get_unit_comment_form(),
            "store": self.store,
            "directory": self.directory,
            "user": self.request.user,
            "project": self.project,
            "language": self.language,
            "source_language": self.source_language,
            "cantranslate": check_user_permission(
                self.request.user, "translate", self.directory
            ),
            "cantranslatexlang": check_user_permission(
                self.request.user, "administrate", self.project.directory
            ),
            "cansuggest": check_user_permission(
                self.request.user, "suggest", self.directory
            ),
            "canreview": check_user_permission(
                self.request.user, "review", self.directory
            ),
            "has_admin_access": check_user_permission(
                self.request.user, "administrate", self.directory
            ),
            "altsrcs": {x.id: x.data for x in self.get_alt_srcs()},
            "unit_values": self.get_unit_values(),
            "target_nplurals": self.get_target_nplurals(),
            "has_plurals": self.object.hasplural(),
        }

    def get_response_data(self, context):
        return {
            "editor": self.render_edit_template(context),
            "tm_suggestions": self.object.get_tm_suggestions()[:MAX_TM_RESULTS],
            "is_obsolete": self.object.isobsolete(),
            "sources": self.get_sources(),
            "target": self.object.target_f.strings,
            "isfuzzy": self.object.isfuzzy(),
        }


@get_unit_context("view")
def permalink_redirect(request, unit):
    return redirect(request.build_absolute_uri(unit.get_translate_url()))


@ajax_required
@get_path_obj
@permission_required("view")
@get_resource
def get_qualitycheck_stats(request, *args, **kwargs):
    failing_checks = request.resource_obj.get_checks()
    if failing_checks is None:
        return JsonResponse({})

    result = [
        dict(count=count, **get_qc_data_by_name(check))
        for check, count in iter(failing_checks.items())
    ]

    def alphabetical_critical_first(item):
        critical_first = 0 if item["is_critical"] else 1
        return critical_first, item["title"].lower()

    result = sorted(result, key=alphabetical_critical_first)
    return JsonResponse(result)


class TPBrowseDataJSON(BaseBrowseDataJSON, TPBrowseView):
    pass


class TPStoreBrowseDataJSON(BaseBrowseDataJSON, TPBrowseStoreView):
    pass


class LanguageBrowseDataJSON(BaseBrowseDataJSON, LanguageBrowseView):
    pass


class ProjectBrowseDataJSON(BaseBrowseDataJSON, ProjectBrowseView):
    pass


class ProjectsBrowseDataJSON(BaseBrowseDataJSON, ProjectsBrowseView):
    pass


class BrowseDataDispatcherView(BasePathDispatcherView):
    language_view_class = LanguageBrowseDataJSON
    store_view_class = TPStoreBrowseDataJSON
    directory_view_class = TPBrowseDataJSON
    project_view_class = ProjectBrowseDataJSON
    projects_view_class = ProjectsBrowseDataJSON


@ajax_required
@get_unit_context("translate")
def submit(request, unit):
    """Processes translation submissions and stores them in the database.

    :return: An object in JSON notation that contains the previous and last
             units for the unit next to unit ``uid``.
    """
    json = {}

    translation_project = request.translation_project
    language = translation_project.language
    old_unit = copy.copy(unit)

    if unit.hasplural():
        snplurals = len(unit.source.strings)
    else:
        snplurals = None

    # Store current time so that it is the same for all submissions
    current_time = timezone.now()

    form_class = unit_form_factory(language, snplurals, request)
    form = form_class(request.POST, instance=unit, request=request)

    if form.is_valid():
        suggestion = form.cleaned_data["suggestion"]
        if suggestion:
            old_unit.accept_suggestion(
                suggestion, request.translation_project, request.user
            )
            if form.cleaned_data["comment"]:
                kwargs = dict(comment=form.cleaned_data["comment"], user=request.user,)
                comment_form = UnsecuredCommentForm(suggestion, kwargs)
                if comment_form.is_valid():
                    comment_form.save()

        if form.updated_fields:
            for field, old_value, new_value in form.updated_fields:
                if field == SubmissionFields.TARGET and suggestion:
                    old_value = str(suggestion.target_f)
                sub = Submission(
                    creation_time=current_time,
                    translation_project=translation_project,
                    submitter=request.user,
                    unit=unit,
                    store=unit.store,
                    field=field,
                    type=SubmissionTypes.NORMAL,
                    old_value=old_value,
                    new_value=new_value,
                    similarity=form.cleaned_data["similarity"],
                    mt_similarity=form.cleaned_data["mt_similarity"],
                )
                sub.save()

            # Update current unit instance's attributes
            # important to set these attributes after saving Submission
            # because we need to access the unit's state before it was saved
            if SubmissionFields.TARGET in (f[0] for f in form.updated_fields):
                form.instance.submitted_by = request.user
                form.instance.submitted_on = current_time
                form.instance.reviewed_by = None
                form.instance.reviewed_on = None

            form.instance._log_user = request.user

            form.save()

            json["checks"] = _get_critical_checks_snippet(request, unit)

        json["user_score"] = request.user.public_score

        return JsonResponse(json)

    return JsonResponseBadRequest({"msg": _("Failed to process submission.")})


@ajax_required
@get_unit_context("suggest")
def suggest(request, unit):
    """Processes translation suggestions and stores them in the database.

    :return: An object in JSON notation that contains the previous and last
             units for the unit next to unit ``uid``.
    """
    json = {}

    translation_project = request.translation_project
    language = translation_project.language

    if unit.hasplural():
        snplurals = len(unit.source.strings)
    else:
        snplurals = None

    form_class = unit_form_factory(language, snplurals, request)
    form = form_class(request.POST, instance=unit, request=request)

    if form.is_valid():
        if form.instance._target_updated:
            # TODO: Review if this hackish method is still necessary
            # HACKISH: django 1.2 stupidly modifies instance on model form
            # validation, reload unit from db
            unit = Unit.objects.get(id=unit.id)
            unit.add_suggestion(
                form.cleaned_data["target_f"],
                user=request.user,
                similarity=form.cleaned_data["similarity"],
                mt_similarity=form.cleaned_data["mt_similarity"],
            )

            json["user_score"] = request.user.public_score

        return JsonResponse(json)

    return JsonResponseBadRequest({"msg": _("Failed to process suggestion.")})


@ajax_required
@require_http_methods(["POST", "DELETE"])
def manage_suggestion(request, uid, sugg_id):
    """Dispatches the suggestion action according to the HTTP verb."""
    if request.method == "DELETE":
        return reject_suggestion(request, uid, sugg_id)
    elif request.method == "POST":
        return accept_suggestion(request, uid, sugg_id)


def handle_suggestion_comment(request, suggestion, unit, comment, action):
    kwargs = {
        "comment": comment,
        "user": request.user,
    }
    comment_form = UnsecuredCommentForm(suggestion, kwargs)
    if comment_form.is_valid():
        comment_form.save()


@get_unit_context()
def reject_suggestion(request, unit, suggid):
    try:
        sugg = unit.suggestion_set.get(id=suggid)
    except ObjectDoesNotExist:
        raise Http404

    # In order to be able to reject a suggestion, users have to either:
    # 1. Have `review` rights, or
    # 2. Be the author of the suggestion being rejected
    if not check_permission("review", request) and (
        request.user.is_anonymous or request.user != sugg.user
    ):
        raise PermissionDenied(_("Insufficient rights to access review mode."))

    unit.reject_suggestion(sugg, request.translation_project, request.user)
    r_data = QueryDict(request.body)
    if "comment" in r_data and r_data["comment"]:
        handle_suggestion_comment(request, sugg, unit, r_data["comment"], "rejected")

    json = {
        "udbid": unit.id,
        "sugid": suggid,
        "user_score": request.user.public_score,
    }
    return JsonResponse(json)


@get_unit_context("review")
def accept_suggestion(request, unit, suggid):
    try:
        suggestion = unit.suggestion_set.get(id=suggid)
    except ObjectDoesNotExist:
        raise Http404

    unit.accept_suggestion(suggestion, request.translation_project, request.user)
    if "comment" in request.POST and request.POST["comment"]:
        handle_suggestion_comment(
            request, suggestion, unit, request.POST["comment"], "accepted"
        )

    json = {
        "udbid": unit.id,
        "sugid": suggid,
        "user_score": request.user.public_score,
        "newtargets": [target for target in unit.target.strings],
        "checks": _get_critical_checks_snippet(request, unit),
    }
    return JsonResponse(json)


@ajax_required
@get_unit_context("review")
def toggle_qualitycheck(request, unit, check_id):
    try:
        unit.toggle_qualitycheck(check_id, "mute" in request.POST, request.user)
    except ObjectDoesNotExist:
        raise Http404

    return JsonResponse({})
