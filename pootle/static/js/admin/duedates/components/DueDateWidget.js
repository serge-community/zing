/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';

import DueDatePicker from './DueDatePicker';

import Dropdown from 'components/Dropdown';
import { formatTimeDelta, formatTimeMessage } from 'utils/time';
import { t } from 'utils/i18n';


function _formatDueTime({ count, unit, isFuture }) {
  const timeMsg = formatTimeMessage(unit, count);
  if (isFuture) {
    return t('Due in %(time)s', { time: timeMsg });
  }
  return t('Overdue by %(time)s', { time: timeMsg });
}

function formatDueTime(msEpoch) {
  return formatTimeDelta(msEpoch, { formatFunction: _formatDueTime });
}


const DueDateWidget = ({ dueOn, id, onRemove, onUpdate }) => {
  let dueOnMsg = t('No due date set');
  let dueOnTooltip = null;
  if (dueOn) {
    dueOnMsg = formatDueTime(dueOn * 1000);
    dueOnTooltip = (new Date(dueOn * 1000)).toUTCString();
  }

  const dropdownTrigger = (
    <a title={dueOnTooltip}>
      {dueOnMsg}
      <span className="icon-desc" />
    </a>
  );

  return (
    <Dropdown trigger={dropdownTrigger}>
      <DueDatePicker
        id={id}
        dueOn={dueOn}
        onRemove={onRemove}
        onUpdate={onUpdate}
      />
    </Dropdown>
  );
};

DueDateWidget.propTypes = {
  dueOn: React.PropTypes.number,
  id: React.PropTypes.number,
  onRemove: React.PropTypes.func.isRequired,
  onUpdate: React.PropTypes.func.isRequired,
};
DueDateWidget.defaultProps = {
  dueOn: 0,
  id: 0,
};


export default DueDateWidget;
