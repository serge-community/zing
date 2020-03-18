# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from django.urls import reverse

from pootle.core.url_helpers import split_pootle_path, to_tp_relative_path
from pootle.i18n.gettext import language_dir, tr_lang
from pootle_store.constants import FUZZY
from pootle_store.unit.proxy import UnitProxy


class UnitResult(UnitProxy):
    @property
    def nplurals(self):
        return self.unit["store__translation_project__language__nplurals"] or 0

    @property
    def pootle_path(self):
        return self.unit["store__pootle_path"]

    @property
    def filename(self):
        return to_tp_relative_path(self.pootle_path)

    @property
    def language_name(self):
        return tr_lang(self.unit["store__translation_project__language__fullname"])

    @property
    def project_code(self):
        return self.unit["store__translation_project__project__code"]

    @property
    def project_name(self):
        return self.unit["store__translation_project__project__fullname"]

    @property
    def project_style(self):
        return self.unit["store__translation_project__project__checkstyle"]

    @property
    def source_dir(self):
        return language_dir(self.source_lang)

    @property
    def source_lang(self):
        return self.unit["store__translation_project__project__source_language__code"]

    @property
    def target_dir(self):
        return language_dir(self.target_lang)

    @property
    def target_lang(self):
        return self.unit["store__translation_project__language__code"]

    @property
    def translate_url(self):
        return u"%s%s" % (
            reverse(
                "pootle-tp-store-translate", args=split_pootle_path(self.pootle_path)
            ),
            "#unit=%s" % str(self.id),
        )

    @property
    def isfuzzy(self):
        return self.state == FUZZY


class ViewRowResults(object):

    select_fields = [
        "id",
        "source_f",
        "target_f",
        "state",
        "store__translation_project__project__source_language__code",
        "store__translation_project__language__code",
        "store__translation_project__language__fullname",
        "store__translation_project__project__fullname",
        "store__pootle_path",
    ]

    def __init__(self, units_qs, header_uids=None):
        self.units_qs = units_qs
        self.header_uids = header_uids if header_uids is not None else []

    @property
    def data(self):
        return {unit.id: self.get_unit_shape(unit) for unit in self.get_units()}

    def get_units(self):
        for values in self.units_qs.values(*self.select_fields):
            yield UnitResult(values)

    def get_unit_shape(self, unit):
        shape = {
            "source": unit.source.strings,
            "source_lang": unit.source_lang,
            "target": unit.target.strings,
            "target_lang": unit.target_lang,
        }

        if unit.id in self.header_uids:
            shape.update(
                {
                    "language": unit.language_name,
                    "project": unit.project_name,
                    "file": unit.filename,
                }
            )

        # We don't need to send default values, so setting members
        # conditionally
        if unit.isfuzzy:
            shape["isfuzzy"] = True
        return shape


class CtxRowResults(ViewRowResults):
    @property
    def data(self):
        return [self.get_unit_shape(unit) for unit in self.get_units()]

    def get_unit_shape(self, unit):
        shape = super().get_unit_shape(unit)
        shape.update({"id": unit.id})
        return shape
