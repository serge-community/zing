# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
#
# This file is a part of the Pootle project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from django.contrib.auth import get_user_model

from pootle.core.url_helpers import split_pootle_path
from pootle.core.utils.stats import (TOP_CONTRIBUTORS_CHUNK_SIZE,
                                     get_top_scorers_data)
from pootle.core.views import BasePathDispatcherView
from pootle.core.views.mixins import PootleJSONMixin
from pootle_language.views import LanguageBrowseView
from pootle_project.views import ProjectBrowseView, ProjectsBrowseView
from pootle_translationproject.views import TPBrowseStoreView, TPBrowseView

from .forms import StatsForm


class ContributorsJSONMixin(PootleJSONMixin):
    @property
    def path(self):
        return self.kwargs["path"]

    def get_context_data(self, **kwargs_):
        User = get_user_model()

        language_code, project_code = split_pootle_path(self.pootle_path)[:2]
        offset = self.kwargs.get("offset", 0)

        top_scorers = User.top_scorers(
            project=project_code,
            language=language_code,
            limit=TOP_CONTRIBUTORS_CHUNK_SIZE + 1,
            offset=offset,
        )

        return get_top_scorers_data(
            top_scorers,
            TOP_CONTRIBUTORS_CHUNK_SIZE
        )


class TPContributorsJSON(ContributorsJSONMixin, TPBrowseView):
    pass


class TPStoreContributorsJSON(ContributorsJSONMixin, TPBrowseStoreView):
    pass


class LanguageContributorsJSON(ContributorsJSONMixin, LanguageBrowseView):
    pass


class ProjectContributorsJSON(ContributorsJSONMixin, ProjectBrowseView):
    pass


class ProjectsContributorsJSON(ContributorsJSONMixin, ProjectsBrowseView):
    pass


class TopContributorsPathDispatcherView(BasePathDispatcherView):
    form_class = StatsForm

    store_view_class = TPStoreContributorsJSON
    directory_view_class = TPContributorsJSON
    language_view_class = LanguageContributorsJSON
    project_view_class = ProjectContributorsJSON
    projects_view_class = ProjectsContributorsJSON
