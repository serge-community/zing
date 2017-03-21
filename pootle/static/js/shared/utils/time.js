/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import { nt, t } from './i18n';


/* Mapping of units and seconds per unit */
const TIMEDELTA_UNITS = {
  year: 365 * 24 * 3600,
  month: 30 * 24 * 3600,
  week: 7 * 24 * 3600,
  day: 24 * 3600,
  hour: 3600, /* 60 * 60 */
  minute: 60,
  second: 1,
};

const TIMEDELTA_THRESHOLDS = {
  year: 0.92, // 11M+
  month: 0.83, // 25d+
  week: 0.86, // 6d+
  day: 0.937, // ~22.5h+
  hour: 0.76,  // 45m+
  minute: 0.76, // 45s+
  second: 1,
};


export function formatTimeMessage(unit, count) {
  if (unit === 'year') {
    if (count === 1) {
      return t('a year');
    }
    return nt('%(count)s year', '%(count)s years', count, { count });
  }

  if (unit === 'month') {
    if (count === 1) {
      return t('a month');
    }
    return nt('%(count)s month', '%(count)s months', count, { count });
  }

  if (unit === 'week') {
    if (count === 1) {
      return t('a week');
    }
    return nt('%(count)s week', '%(count)s weeks', count, { count });
  }

  if (unit === 'day') {
    if (count === 1) {
      return t('a day');
    }
    return nt('%(count)s day', '%(count)s days', count, { count });
  }

  if (unit === 'hour') {
    if (count === 1) {
      return t('an hour');
    }
    return nt('%(count)s hour', '%(count)s hours', count, { count });
  }

  if (unit === 'minute') {
    if (count === 1) {
      return t('a minute');
    }
    return nt('%(count)s minute', '%(count)s minutes', count, { count });
  }

  return t('a few seconds');
}


/**
 * Formats the time difference from `msEpoch` to the current date as
 * provided by the client.
 */
function formatUnit({ count, unit, addDirection, isFuture }) {
  const timeMsg = formatTimeMessage(unit, count);
  if (!addDirection) {
    return timeMsg;
  }

  if (isFuture) {
    return t('in %(time)s', { time: timeMsg });
  }
  return t('%(time)s ago', { time: timeMsg });
}


/**
 * Formats the time difference from `msEpoch` to the current date as
 * provided by the client.
 *
 *
 * @param {String} msEpoch - Number of milliseconds since epoch.
 * @param {Boolean} addDirection - Whether to format using past/future
 *   markers (`%s ago`, `in %s`). Defaults to `false`.
 * @param {Function} formatFunction - alternative time formatting function.
 *   If none is provided, `formatUnit` will be used.
 * @return {String} - A formatted string of the time difference since `msEpoch`.
 */
export function formatTimeDelta(
  msEpoch, { addDirection = false, formatFunction = null } = {}
) {
  const now = Date.now();
  const delta = msEpoch - now;
  const seconds = Math.abs(delta / 1000);

  const formatter = (
    typeof formatFunction === 'function' ? formatFunction : formatUnit
  );
  let formatted = '';

  const units = Object.keys(TIMEDELTA_UNITS);
  // Using regular for as `forEach()` doesn't support breaking
  for (let i = 0; i < units.length; i++) {
    const unit = units[i];
    const value = (seconds / TIMEDELTA_UNITS[unit]).toFixed(3);
    const threshold = TIMEDELTA_THRESHOLDS[unit];

    if (value >= threshold) {
      const count = Math.round(value);
      formatted = formatter({ count, unit, addDirection, isFuture: delta > 0 });
      break;
    }
  }

  return formatted;
}


/**
 * Converts a `Date` object `localDate` into the server's timezone.
 *
 * @param Date localDate a Date object, represented in the local timezone.
 * @param Integer serverUtcOffset server's offset with respect to UTC,
 *   in seconds.
 * @return Date `localDate` localized to server's timezone.
 */
export function toServerDate(localDate, {
    serverUtcOffset = PTL.settings.TZ_OFFSET,
  } = {}
) {
  const localUtcOffsetMs = localDate.getTimezoneOffset() * 60 * 1000;
  const utcMs = localDate.getTime() - localUtcOffsetMs;
  const serverUtcOffsetMs = serverUtcOffset * 1000;
  return new Date(utcMs + serverUtcOffsetMs);
}


/**
 * Sets a `Date` object's hours according to the server's timezone.
 *
 * @param Date date a Date object, represented in the server's timezone.
 * @param Integer serverUtcOffset server's offset with respect to UTC,
 *   in seconds.
 * @return Date a given date's copy adjusted to `hours` in server's timezone.
 */
export function setServerHours(serverDate, hours, minutes = null, {
    serverUtcOffset = PTL.settings.TZ_OFFSET,
  } = {}
) {
  const newDate = new Date(serverDate.getTime());
  const hoursOffset = serverUtcOffset / (60 * 60);
  const newUTCHours = (hours - hoursOffset);
  newDate.setUTCHours(newUTCHours);

  if (minutes !== null) {
    newDate.setUTCMinutes(minutes);
  }

  return newDate;
}
