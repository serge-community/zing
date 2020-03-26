/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';

import TranslateActions from './TranslateActions';
import DueDateContainer from '../../admin/duedates/components/DueDateContainer';


// TODO: after upgrading React:
//  1. use React.Fragment
//  2. load DueDateContainer via React.lazy
const ActionBar = ({
  areTranslateActionsEnabled, canAdminDueDates, initialDueDate, pootlePath, totalStats,
}) => (
    <div>
      <TranslateActions
        areActionsEnabled={areTranslateActionsEnabled}
        pootlePath={pootlePath}
        totalStats={totalStats}
      />
      {canAdminDueDates &&
        <ul>
          <li>
            <DueDateContainer initialDueDate={initialDueDate} />
          </li>
        </ul>
      }
    </div>
  );
ActionBar.propTypes = {
  areTranslateActionsEnabled: React.PropTypes.bool,
  canAdminDueDates: React.PropTypes.bool,
  initialDueDate: React.PropTypes.shape({
    id: React.PropTypes.number,
    due_on: React.PropTypes.number,
    pootle_path: React.PropTypes.string,
  }),
  pootlePath: React.PropTypes.string.isRequired,
  totalStats: React.PropTypes.shape({
    critical: React.PropTypes.number,
    suggestions: React.PropTypes.number,
    total: React.PropTypes.number.isRequired,
    translated: React.PropTypes.number.isRequired,
  }),
};

export default ActionBar;
