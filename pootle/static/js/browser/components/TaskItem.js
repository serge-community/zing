/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';

import { dueTime } from 'utils/dueTime';
import { t, tct } from 'utils/i18n';
import { getResourcePath, getTranslateUrl } from 'utils/url';


const TaskItem = ({ path, projectName, wordsLeft, dueOnMsEpoch, type }) => {
  let label;
  let actionUrl = getTranslateUrl(path);

  if (type === 'critical') {
    label = t('Fix critical errors');
    actionUrl = `${actionUrl}#filter=checks&category=critical`;
  } else {
    label = t('Finish translation');
    actionUrl = `${actionUrl}#filter=incomplete`;
  }

  const dueDate = new Date(dueOnMsEpoch);
  const dueDateMsg = dueDate.toISOString();
  const dueDateTooltip = dueDateMsg;

  const taskComp = (
    <span className={`task-action task-${type}`}>
      <span>{label}</span>
      <span className="counter">{wordsLeft}</span>
    </span>
  );
  const resourcePath = getResourcePath(path);
  const projectComp = (
    <span>{projectName}{resourcePath && ` ${resourcePath}`}</span>
  );
  const dateComp = (
    <span
      className="due-on"
      title={dueDateTooltip}
    >{dueDateMsg}</span>
  );
  // TODO: provide due date picker when `hasAdminAccess` is true
  const dueOnComp = (
    <span
      className="due-on"
    >{dueTime(dueOnMsEpoch)}</span>
  );

  return (
    <a className="task-item" href={actionUrl}>
      {tct('Next: %(task)s in %(project)s by %(date)s (%(dueOn)s)', {
        task: taskComp,
        project: projectComp,
        date: dateComp,
        dueOn: dueOnComp,
      })}
    </a>
  );
};
TaskItem.propTypes = {
  dueOnMsEpoch: React.PropTypes.number.isRequired,
  path: React.PropTypes.string.isRequired,
  projectName: React.PropTypes.string.isRequired,
  type: React.PropTypes.string.isRequired,
  wordsLeft: React.PropTypes.number.isRequired,
};


export default TaskItem;
