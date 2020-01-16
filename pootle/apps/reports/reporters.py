# -*- coding: utf-8 -*-
#
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import codecs
import json
import logging
import os
import re

from django.conf import settings
from django.utils.timezone import now


logger = logging.getLogger(__name__)


class BaseReporter(object):

    def __init__(self, *args, **kwargs):
        self.generated_at = now().replace(microsecond=0)
        self.invoices = []

    def add(self, invoice):
        self.invoices.append(invoice)

    def generate(self, **kwargs):
        raise NotImplementedError


class JSONReporter(BaseReporter):

    @property
    def filepath(self):
        try:
            month_string = self.invoices[0].month_string
        except IndexError:
            raise RuntimeError('Attempted to run generation with no invoices')

        month_dir = os.path.join(settings.ZING_INVOICES_DIRECTORY, month_string)
        return os.path.join(month_dir, 'report.json')

    def clean_config_value(self, value):
        if not isinstance(value, basestring):
            return value
        return re.sub('\n\s+', '\n', value)

    def get_invoice_data(self, invoice):
        """Gets individual invoice data."""
        return {
            'id': invoice.id,
            'amount': invoice.amounts['total'],
            'vendor': {
                key: self.clean_config_value(value)
                for key, value in iter(invoice.conf.items())
            },
        }

    def get_data(self):
        """Gets a dictionary to be consumed by the report generation."""
        return {
            'generated_at': self.generated_at.isoformat(),
            'invoices': [
                self.get_invoice_data(invoice) for invoice in self.invoices
            ],
        }

    def generate(self, **kwargs):
        """Generates a JSON report of this invoicing job."""
        report_data = self.get_data()
        report = json.dumps(
            report_data, indent=4, sort_keys=True, separators=(',', ': ')
        )
        codecs.open(self.filepath, 'w', 'utf-8').write(report)
        return True
