/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';

import TaskItem from './TaskItem';


const TaskListItem = ({ importanceFactor, children }) => {
  const style = {
    backgroundColor: `hsl(15, ${Math.round(importanceFactor * 100)}%, 40%)`,
  };
  return (
    <li style={style}>{children}</li>
  );
};
TaskListItem.propTypes = {
  children: React.PropTypes.element.isRequired,
  importanceFactor: React.PropTypes.number.isRequired,
};


const TaskList = ({ tasks }) => (
  <ul className="pending-tasks">
    {tasks.map((task, i) => (
      <TaskListItem
        key={i}
        importanceFactor={task.importance_factor}
      >
        <TaskItem
          dueDateId={task.due_date_id}
          dueOnMsEpoch={task.due_on * 1000}
          path={task.path}
          projectName={task.project_name}
          type={task.type}
          wordsLeft={task.words_left}
        />
      </TaskListItem>
    ))}
  </ul>
);
TaskList.propTypes = {
  tasks: React.PropTypes.array.isRequired,
};


export default TaskList;
