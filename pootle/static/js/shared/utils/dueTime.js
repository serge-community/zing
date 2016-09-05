/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import { nt, t } from './i18n';
import { timeDelta } from './time';


export function _dueTimeMessage({ hours, days, weeks, months, years }) {
  if (years > 0) {
    return nt('Due in %(count)s year', 'Due in %(count)s years',
              years, { count: years });
  } else if (months > 0) {
    return nt('Due in %(count)s month', 'Due in %(count)s months',
              months, { count: months });
  } else if (weeks > 0) {
    return nt('Due in %(count)s week', 'Due in %(count)s weeks',
              weeks, { count: weeks });
  } else if (days > 0) {
    return nt('Due in %(count)s day', 'Due in %(count)s days',
              days, { count: days });
  } else if (hours > 1) {
    return nt('Due in %(count)s hour', 'Due in %(count)s hours',
              hours, { count: hours });
  }

  return t('Due right now');
}


export function _overdueTimeMessage({ hours, days, weeks, months, years }) {
  if (years > 0) {
    return nt('Overdue by %(count)s year', 'Overdue by %(count)s years',
              years, { count: years });
  } else if (months > 0) {
    return nt('Overdue by %(count)s month', 'Overdue by %(count)s months',
              months, { count: months });
  } else if (weeks > 0) {
    return nt('Overdue by %(count)s week', 'Overdue by %(count)s weeks',
              weeks, { count: weeks });
  } else if (days > 0) {
    return nt('Overdue by %(count)s day', 'Overdue by %(count)s days',
              days, { count: days });
  } else if (hours > 1) {
    return nt('Overdue by %(count)s hour', 'Overdue by %(count)s hours',
              hours, { count: hours });
  }

  return t('Overdue right now');
}


export function dueTime(msEpoch) {
  const { isFuture, hours, days, weeks, months, years } = timeDelta(msEpoch);

  if (isFuture === null) {
    return '';
  }

  if (isFuture) {
    return _dueTimeMessage({ hours, days, weeks, months, years });
  }

  return _overdueTimeMessage({ hours, days, weeks, months, years });
}
