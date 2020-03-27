/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';


const RTL_LANGUAGES = [
  'aao',
  'abh',
  'abv',
  'acm',
  'acq',
  'acw',
  'acx',
  'acy',
  'adf',
  'ads',
  'aeb',
  'aec',
  'afb',
  'ajp',
  'apc',
  'apd',
  'ar',
  'arb',
  'arc',
  'arq',
  'ars',
  'ary',
  'arz',
  'auz',
  'avl',
  'ayh',
  'ayl',
  'ayn',
  'ayp',
  'bbz',
  'bcc',
  'bqi',
  'ckb',
  'dv',
  'fa',
  'glk',
  'hbo',
  'he',
  'iw',
  'ji',
  'jpr',
  'ks',
  'lrc',
  'men',
  'mzn',
  'nqo',
  'pbt',
  'pbu',
  'peo',
  'pes',
  'pga',
  'pnb',
  'prd',
  'prp',
  'prs',
  'ps',
  'pst',
  'sam',
  'sd',
  'shu',
  'sqr',
  'ssh',
  'ug',
  'ur',
  'xaa',
  'xmn',
  'ydd',
  'yds',
  'yhd',
  'yi',
  'yih',
  'yud',
];


/**
 * Make it possible React components can be added as placeholders.
 *
 * Example:
 * `formatComponent(%(foo)s bar %(baz)s)` returns `[ctx.foo, bar, ctx.baz]` list.
 */
function formatComponent(str, ctx) {
  const result = [];
  let id = 0;
  let _fmt = str;
  let match = [];

  while (_fmt) {
    match = /^[^\x25]+/.exec(_fmt);
    if (match !== null) {
      result.push(match[0]);
    } else {
      match = /^\x25\(([^\)]+)\)s/.exec(_fmt);
      if (match === null) {
        throw new Error('Wrong format');
      }
      if (match[1]) {
        const arg = ctx[match[1]];
        if (React.isValidElement(arg)) {
          result.push(React.cloneElement(arg, { key: id++ }));
        } else {
          result.push(arg);
        }
      }
    }
    _fmt = _fmt.substring(match[0].length);
  }
  return result;
}


/**
 * Mark a string for localization and optionally replace placeholders with the
 * components provided in the context argument. This is intended to use in the
 * context of JSX and React components.
 *
 * @param {String} string - The string to internationalize. It accepts a
 * simplified form of printf-style placeholders, however note these must be
 * named, so they need to take the explicit `%(key)s` form, not `%s`.
 * @param {Object} ctx - Components to be injected in the placeholders specified
 * by the keys.
 * @return {Array} - An array with the original `string`, and placeholders
 * replaced by the given components.
 */
export function tct(string, ctx = null) {
  if (!ctx) {
    return [gettext(string)];
  }
  return formatComponent(gettext(string), ctx);
}


/**
 * Mark a string for localization and optionally replace placeholders with the
 * values provided in the context argument.
 *
 * @param {String} string - The string to internationalize. It accepts a
 * simplified form of printf-style placeholders, however note these must be
 * named, so they need to take the explicit `%(key)s` form, not `%s`.
 * @param {Object} ctx - Values to be injected in the placeholders specified by
 * the keys. Note these will be coerced to strings.
 * @return {String} - The original `string` with placeholders replaced by the
 * given context values.
 */
export function t(string, ctx = null) {
  if (!ctx) {
    return gettext(string);
  }
  return interpolate(gettext(string), ctx, true);
}


/**
 * Mark a plural string for localization and optionally replace placeholders
 * with the values provided in the context argument.
 *
 * @param {String} singular - The singular string to internationalize. It
 * accepts the same placeholders as `t()`.
 * @param {String} plural - The plural string to internationalize. It accepts
 * the same placeholders as `t()`.
 * @param {Integer} count - The object count which will determine the
 * translation string o use.
 * @param {Object} ctx - Values to be injected in the placeholders specified by
 * the keys. Note these will be coerced to strings.
 * @return {String} - The translation for `singular` or `plural` (depending on
 * `count`) with placeholders replaced by the given context values.
 */
export function nt(singular, plural, count, ctx = null) {
  if (!ctx) {
    return ngettext(singular, plural, count);
  }
  return interpolate(ngettext(singular, plural, count), ctx, true);
}


/**
 * Locale-specific to-string conversion.
 *
 * This is a thin wrapper around `.toLocaleString()` to always use
 * `navigator.language`, which is the least bad option we have to determine
 * user's preferred language for the time being.
 *
 * Please note browsers implement `toLocaleString()` very differently and when
 * it comes to number decimals, it doesn't work at all in Safari 9 and Edge,
 * Chrome always omits the parameter passed to `toLocaleString()` and Firefox is
 * the only one obeying it.
 */
export function toLocaleString(number) {
  return number.toLocaleString(navigator.language);
}


export const dateFormatter = new Intl.DateTimeFormat(PTL.settings.UI_LOCALE, {
  month: 'long',
  day: 'numeric',
});


// Flag needed for Edge as it doesn't support the `timeZone` option
let isTzSupported = true;
try {
  (new Date()).toLocaleString('en', { timeZone: 'Europe/Amsterdam' });
} catch (e) {
  isTzSupported = !(e instanceof RangeError);
}

let userTimeZone = (new Intl.DateTimeFormat()).resolvedOptions().timeZone;

// In older Android+Webkit browsers, the timezone might be reported as an
// abbreviation (e.g. 'CET'), but Intl formatting functions require timezone
// names as they appear in the IANA DB. In such cases, fall back to the server
// timezone to avoid breakage.
if (userTimeZone.indexOf('/') === -1 &&
    ['UTC', 'GMT'].indexOf(userTimeZone) === -1) {
  // eslint-disable-next-line no-console
  console.log(
    'Intl.timeZone: got a timezone not compliant with the IANA DB: ',
    userTimeZone
  );
  userTimeZone = PTL.settings.TZ;
}

const tzOptions = isTzSupported ? {
  timeZone: userTimeZone,
  timeZoneName: 'short',
} : {};

export const dateTimeTzFormatter = new Intl.DateTimeFormat(
  PTL.settings.UI_LOCALE,
  Object.assign({}, {
    month: 'long',
    day: 'numeric',
    hour: 'numeric',
    minute: 'numeric',
  }, tzOptions)
);

const serverTzOptions = isTzSupported ? {
  timeZone: PTL.settings.TZ,
  timeZoneName: 'short',
} : {};

export const serverDateTimeTzFormatter = new Intl.DateTimeFormat(
  PTL.settings.UI_LOCALE,
  Object.assign({}, {
    month: 'long',
    day: 'numeric',
    hour: 'numeric',
    minute: 'numeric',
  }, serverTzOptions)
);

export const serverTimeTzFormatter = new Intl.DateTimeFormat(
  PTL.settings.UI_LOCALE,
  Object.assign({}, {
    hour: 'numeric',
    minute: 'numeric',
  }, serverTzOptions)
);


/**
 * Helper to determine the directionality for a language.
 *
 * @param {String} langCode - The language code of the language to check.
 * @return {String} - 'rtl' for a language using a RTL script, 'ltr' otherwise.
 */
export function dir(langCode) {
  return RTL_LANGUAGES.indexOf(langCode) !== -1 ? 'rtl' : 'ltr';
}
