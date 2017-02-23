/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */


/**
 * Retrieves a translation URL out of an internal `path`
 * @param {string} path - internal path
 */
export function getTranslateUrl(path) {
  const pathItems = path.split('/'); // path starts with the slash
  pathItems.shift(); // remove the first empty item
  const lang = pathItems.shift();
  const project = pathItems.shift();
  return `/${lang}/${project}/translate/${pathItems.join('/')}`;
}
