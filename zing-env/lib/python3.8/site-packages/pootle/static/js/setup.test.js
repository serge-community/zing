/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

global.gettext = string => string;

global.ngettext = (singular, plural, count) => (
  (count === 1) ? singular : plural
);

global.interpolate = (string, args) => (
  string.replace(/%\(\w+\)s/g, (match) => String(args[match.slice(2, -2)]))
);

global.PTL = {
  settings: {
    UI_LOCALE: 'en',
  },
};
