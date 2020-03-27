/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import { t } from 'utils/i18n';
import { formatTimeDelta, formatTimeMessage } from 'utils/time';

function _formatDueTime({ count, unit, isFuture }) {
  const timeMsg = formatTimeMessage(unit, count);
  if (isFuture) {
    return t('Due in %(time)s', { time: timeMsg });
  }
  return t('Overdue by %(time)s', { time: timeMsg });
}

export function formatDueTime(msEpoch) {
  return formatTimeDelta(msEpoch, { formatFunction: _formatDueTime });
}
