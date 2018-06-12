# -*- coding: utf-8 -*-
#
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import logging
import os
from subprocess import check_output, CalledProcessError

from django.conf import settings
from django.core import management
from django.core.management.base import BaseCommand, CommandError

from . import SkipChecksMixin

logger = logging.getLogger(__name__)


class Command(SkipChecksMixin, BaseCommand):
    help = "Builds static assets."
    skip_system_check_tags = ('data', )

    def handle(self, **options):
        self.pkg_dir = os.path.dirname(
            os.path.dirname(
                os.path.dirname(
                    os.path.dirname(os.path.dirname(__file__))
                )
            )
        )
        self.static_dir = os.path.join(self.pkg_dir, 'static')
        self.js_dir = os.path.join(self.static_dir, 'js')

        self.stdout.write('Building static files...')

        self._setup_npm()
        self._setup_dirs()
        self._build()

    def _run(self, cmd, **kwargs):
        try:
            return check_output(cmd, **kwargs)
        except CalledProcessError as e:
            raise CommandError(
                'Could not run %r: %s' % (cmd, e)
            )

    def _setup_npm(self):
        versions = []

        for binary in ('node', 'npm'):
            try:
                versions.append(self._run([binary, '--version']).rstrip())
            except OSError:
                raise CommandError(
                    'Cannot find `%s` executable. Please install it and retry.' %
                    binary
                )

        logger.info('using node (%s) and npm (%s)', *versions)

        self._run(['npm', 'install', '--quiet'], cwd=self.js_dir)

    def _setup_dirs(self):
        assets_dir = os.path.join(self.pkg_dir, 'assets')
        try:
            os.mkdir(assets_dir)
        except OSError:
            pass

    def _build(self):
        env = dict(os.environ)
        env['NODE_ENV'] = 'production'

        self._run(['node_modules/.bin/webpack', '--bail'],
                  cwd=self.js_dir, env=env)

        # HACK: temporarily modify where assets will be built to, otherwise
        # `collectstatic` needs to be run twice
        cfg_root = settings.STATIC_ROOT
        settings.STATIC_ROOT = self.static_dir
        management.call_command('assets', 'build')
        settings.STATIC_ROOT = cfg_root
        management.call_command(
            'collectstatic', '--clear', '--noinput', '-i', 'node_modules'
        )
