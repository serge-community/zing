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
import DropdownMenu from 'components/DropdownMenu';
import DropdownToggle from 'components/DropdownToggle';
import { t, serverDateTimeTzFormatter } from 'utils/i18n';

import { formatDueTime } from '../utils';


const propTypes = {
  dueOn: React.PropTypes.number,
  id: React.PropTypes.number,
  isOpen: React.PropTypes.bool.isRequired,
  onRemove: React.PropTypes.func.isRequired,
  onToggle: React.PropTypes.func.isRequired,
  onUpdate: React.PropTypes.func.isRequired,
};

const defaultProps = {
  dueOn: 0,
  id: 0,
};


const DueDateWidget = ({ dueOn, id, isOpen, onRemove, onToggle, onUpdate }) => {
  let dueOnMsg = t('No due date set');
  let dueOnTooltip = null;
  if (dueOn) {
    dueOnMsg = formatDueTime(dueOn * 1000);
    dueOnTooltip = serverDateTimeTzFormatter.format(dueOn * 1000);
  }

  return (
    <Dropdown isOpen={isOpen} onToggle={onToggle}>
      <DropdownToggle title={dueOnTooltip}>
        {dueOnMsg}
      </DropdownToggle>
      <DropdownMenu>
        <DueDatePicker
          id={id}
          dueOn={dueOn}
          onRemove={onRemove}
          onUpdate={onUpdate}
        />
      </DropdownMenu>
    </Dropdown>
  );
};

DueDateWidget.propTypes = propTypes;
DueDateWidget.defaultProps = defaultProps;


export default DueDateWidget;
