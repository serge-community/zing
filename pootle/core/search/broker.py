# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import importlib
import logging

from . import SearchBackend


class SearchBroker(SearchBackend):

    def __init__(self):
        super(SearchBroker, self).__init__()
        self._server = None

        if self._settings is None:
            return

        if 'HOST' not in self._settings or 'PORT' not in self._settings:
            return

        try:
            _module = '.'.join(self._settings['ENGINE'].split('.')[:-1])
            _search_class = self._settings['ENGINE'].split('.')[-1]
        except KeyError:
            logging.warning("The TM search backend is missing the "
                            "required 'ENGINE' setting")
            return
        try:
            module = importlib.import_module(_module)
            try:
                self._server = getattr(module, _search_class)()
            except AttributeError:
                logging.warning("No search class '%s' defined.", _search_class)
        except ImportError:
            logging.warning("TM search backend: cannot import '%s'", _module)

    def search(self, unit):
        if not self._server:
            return []

        results = []
        counter = {}
        for result in self._server.search(unit):
            translation_pair = result['source'] + result['target']
            if translation_pair not in counter:
                counter[translation_pair] = result['count']
                results.append(result)
            else:
                counter[translation_pair] += result['count']

        for item in results:
            item['count'] = counter[item['source']+item['target']]

        # Results are in the order of the TM servers, so they must be sorted by
        # score so the better matches are presented to the user.
        results = sorted(results, reverse=True,
                         key=lambda item: item['score'])

        return results

    def update(self, language, obj):
        if not self._server:
            return

        self._server.update(language, obj)
