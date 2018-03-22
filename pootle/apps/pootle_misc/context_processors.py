# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from django.conf import settings
from django.utils import timezone, translation

from pootle.core.constants import CACHE_TIMEOUT
from pootle_language.models import Language
from pootle_project.models import Project
from staticpages.models import LegalPage


local_now = timezone.localtime(timezone.now())
TZ_OFFSET = local_now.utcoffset().total_seconds()


def _agreement_context(request):
    """Returns whether the agreement box should be displayed or not."""
    request_path = request.META['PATH_INFO']
    nocheck = filter(lambda x: request_path.startswith(x),
                     settings.POOTLE_LEGALPAGE_NOCHECK_PREFIXES)

    if (request.user.is_authenticated and not nocheck and
        LegalPage.objects.has_pending_agreement(request.user)):
        return True

    return False


def _get_social_auth_providers(request):
    if 'allauth.socialaccount' not in settings.INSTALLED_APPS:
        return []

    from allauth.socialaccount import providers
    return [{'name': provider.name, 'url': provider.get_login_url(request)}
            for provider in providers.registry.get_list()]


def pootle_context(request):
    """Exposes settings to templates."""
    # FIXME: maybe we should expose relevant settings only?
    return {
        'settings': {
            'POOTLE_TITLE': settings.POOTLE_TITLE,
            'POOTLE_INSTANCE_ID': settings.POOTLE_INSTANCE_ID,
            'POOTLE_SIGNUP_ENABLED': settings.POOTLE_SIGNUP_ENABLED,
            'CACHE_TIMEOUT': CACHE_TIMEOUT,
            'CAN_CONTACT': bool(settings.ZING_CONTACT_EMAIL.strip()),
            'TZ': settings.TIME_ZONE,
            'TZ_OFFSET': TZ_OFFSET,
            'DEBUG': settings.DEBUG,
        },
        'ALL_LANGUAGES': Language.live.cached_dict(translation.get_language(),
                                                   request.user.is_superuser),
        'ALL_PROJECTS': Project.objects.cached_dict(request.user),
        'SOCIAL_AUTH_PROVIDERS': _get_social_auth_providers(request),
        'display_agreement': _agreement_context(request),
    }
