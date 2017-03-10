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
import { t, dateTimeTzFormatter } from 'utils/i18n';

import { formatDueTime } from '../utils';


const DueDateWidget = ({ dueOn, id, onRemove, onUpdate }) => {
  let dueOnMsg = t('No due date set');
  let dueOnTooltip = null;
  if (dueOn) {
    dueOnMsg = formatDueTime(dueOn * 1000);
    dueOnTooltip = dateTimeTzFormatter.format(dueOn * 1000);
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
