/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';

import { t, tct, dateFormatter, dateTimeTzFormatter } from 'utils/i18n';
import { formatTimeDelta, formatTimeMessage } from 'utils/time';
import { getResourcePath, getTranslateUrl } from 'utils/url';


function _formatDueTime({ count, unit, isFuture }) {
  if (unit === 'minute' && count < 30) {
    return t('due right now');
  }

  const timeMsg = formatTimeMessage(unit, count);
  if (isFuture) {
    return t('in %(time)s', { time: timeMsg });
  }
  return t('%(time)s late', { time: timeMsg });
}

function formatDueTime(msEpoch) {
  return formatTimeDelta(msEpoch, { formatFunction: _formatDueTime });
}


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

  const dueDateMsg = dateFormatter.format(dueOnMsEpoch);
  const dueDateTooltip = dateTimeTzFormatter.format(dueOnMsEpoch);

  const taskComp = (
    <span className={`task-action task-${type}`}>
      <span>{label}</span>
      <span className="counter">{wordsLeft}</span>
    </span>
  );
  const resourcePath = getResourcePath(path);
  const projectComp = resourcePath ? (
    t('%(projectName)s → %(resourcePath)s', { projectName, resourcePath })
  ) : (
     <span>{projectName}</span>
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
    >{formatDueTime(dueOnMsEpoch)}</span>
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
