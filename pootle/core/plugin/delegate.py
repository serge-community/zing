# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
#
# This file is a part of the Pootle project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from django.dispatch import Signal
from django.dispatch.dispatcher import NO_RECEIVERS


class Getter(Signal):

    def get(self, sender=None, **named):
        no_receivers = (
            not self.receivers
            or self.sender_receivers_cache.get(sender) is NO_RECEIVERS)
        if no_receivers:
            return None
        for receiver in self._live_receivers(sender):
            response = receiver(signal=self, sender=sender, **named)
            if response is not None:
                return response


def getter(signal, **kwargs):
    def _decorator(func):
        if isinstance(signal, (list, tuple)):
            for s in signal:
                s.connect(func, **kwargs)
        else:
            signal.connect(func, **kwargs)
        return func
    return _decorator
