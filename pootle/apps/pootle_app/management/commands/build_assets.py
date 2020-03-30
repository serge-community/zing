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

from django.core import management
from django.core.management.base import BaseCommand, CommandError

from . import SkipChecksMixin

logger = logging.getLogger(__name__)


class Command(SkipChecksMixin, BaseCommand):
    help = "Builds static assets."
    skip_system_check_tags = ("data",)

    def handle(self, **options):
        self.pkg_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        )
        self.static_dir = os.path.join(self.pkg_dir, "static")
        self.js_dir = os.path.join(self.static_dir, "js")
        self.target_dir = os.path.join(self.pkg_dir, "assets")

        self.stdout.write("Building static files...")

        self._setup_npm()
        self._setup_dirs()
        self._build()

    def _run(self, cmd, **kwargs):
        try:
            return check_output(cmd, encoding="utf-8", **kwargs)
        except CalledProcessError as e:
            raise CommandError("Could not run %r: %s" % (cmd, e))

    def _setup_npm(self):
        versions = []

        for binary in ("node", "npm"):
            try:
                versions.append(self._run([binary, "--version"]).rstrip())
            except OSError:
                raise CommandError(
                    "Cannot find `%s` executable. Please install it and retry." % binary
                )

        logger.info("using node (%s) and npm (%s)", *versions)

        self._run(["npm", "install", "--quiet"], cwd=self.js_dir)

    def _setup_dirs(self):
        try:
            os.mkdir(self.target_dir)
        except OSError:
            pass

    def _build(self):
        env = dict(os.environ)
        env["NODE_ENV"] = "production"

        try:
            self._run(["node_modules/.bin/webpack", "--bail"], cwd=self.js_dir, env=env)
        except OSError:
            raise CommandError(
                "Cannot find `webpack` executable. Please make sure your node "
                "version is recent enough and retry."
            )

        management.call_command("compilejsi18n")
        management.call_command(
            "collectstatic", "--clear", "--noinput", "-i", "node_modules"
        )
        manifest_file = os.path.join(self.static_dir, "manifest.json")
        management.call_command(
            "assets", "build", "--manifest", "json:%s" % manifest_file
        )
