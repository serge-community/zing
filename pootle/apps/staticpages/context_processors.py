# -*- coding: utf-8 -*-
#
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from .models import LegalPage


NOCHECK_PREFIXES = (
    '/about',
    '/accounts',
    '/admin',
    '/contact',
    '/jsi18n',
    '/pages',
    '/xhr',
)


def agreement(request):
    """Returns whether the agreement box should be displayed or not."""
    request_path = request.META['PATH_INFO']
    nocheck = filter(lambda x: request_path.startswith(x), NOCHECK_PREFIXES)

    display_agreement = False
    if (request.user.is_authenticated and not nocheck and
        LegalPage.objects.has_pending_agreement(request.user)):
        display_agreement = True

    return {
        'display_agreement': display_agreement,
    }
