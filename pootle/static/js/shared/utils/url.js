/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

/**
 * Split a string while returning the remainder.
 *
 * Note JS's `String.prototype.split` method unfortunately doesn't
 * return the remainder in the last index in case a limit parameter
 * was specified.
 */
export function split(value, separator, limit) {
  const parts = value.split(separator);

  if (parts.length <= limit) {
    return parts;
  }
  return parts.splice(0, limit).concat(parts.join(separator));
}

/**
 * Splits an internal path into language, project, directory and file parts.
 * @param {string} path - internal path
 * @return {array} - [lang_code, proj_code, dir_path, filename]
 */
export function splitPootlePath(path) {
  const slashCount = path.split('/').length - 1;
  const parts = split(path, '/', 3).slice(1);

  let languageCode = null;
  let projectCode = null;
  let ctx = '';

  if (slashCount !== 0 && path !== '/projects/') {
    if (slashCount === 2) {
      languageCode = parts[0];
    } else if (path.startsWith('/projects/')) {
      projectCode = parts[1];
      ctx = parts[2];
    } else if (slashCount !== 1) {
      languageCode = parts[0];
      projectCode = parts[1];
      ctx = parts[2];
    }
  }

  const lastSlash = ctx.lastIndexOf('/');
  const dirPath = ctx.substring(0, lastSlash + 1);
  const filename = ctx.substring(lastSlash + 1, ctx.length);

  return [languageCode, projectCode, dirPath, filename];
}

/**
 * Retrieves the path to a resource path out of an internal `path`.
 * @param {string} path - internal path
 */
export function getResourcePath(path) {
  const [, , dirPath, filename] = splitPootlePath(path);
  return dirPath + filename;
}

/**
 * Retrieves a translation URL out of an internal `path`
 * @param {string} path - internal path
 */
export function getTranslateUrl(path, { checks, checksCategory, filter } = {}) {
  const [languageCode, projectCode, dirPath, filename] = splitPootlePath(path);

  let url;
  if (languageCode && projectCode) {
    url = `/${languageCode}/${projectCode}`;
  } else if (languageCode) {
    url = `/${languageCode}`;
  } else if (projectCode) {
    url = `/projects/${projectCode}`;
  } else {
    url = '/projects';
  }

  url += `/translate/${dirPath + filename}`;

  if (filter) {
    return `${url}#filter=${filter}`;
  }

  if (checks) {
    return `${url}#filter=checks&checks=${checks}`;
  }

  if (checksCategory) {
    return `${url}#filter=checks&category=${checksCategory}`;
  }

  return url;
}
