/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';

import TaskAPI from 'api/TaskAPI';
import { nt } from 'utils/i18n';

import TaskList from './TaskList';


class PendingTaskContainer extends React.Component {

  constructor(props) {
    super(props);

    this.state = {
      tasks: props.tasks,
    };
  }

  componentWillReceiveProps(nextProps) {
    if (nextProps.hasOwnProperty('tasks')) {
      this.setState({ tasks: nextProps.tasks });
    }
  }

  handleLoadMore(e) {
    e.preventDefault();

    const params = { offset: this.state.tasks.length };
    return TaskAPI.get(this.props.languageCode, params)
      .done((data) => {
        this.setState((prevState) => {
          const newItems = prevState.tasks.concat(data.items);
          return {
            tasks: newItems,
          };
        });
      });
  }

  renderLoadMore() {
    const remaining = this.props.total - this.state.tasks.length;
    if (remaining === 0) {
      return null;
    }

    const loadMoreMsg = nt('%(n)s more task', '%(n)s more tasks',
                           remaining, { n: remaining });
    return (
      <div className="task-action-expand" onClick={(e) => this.handleLoadMore(e)}>
        <span>{loadMoreMsg}</span>
        {' '}
        <i className="icon-expand-tasks" />
      </div>
    );
  }

  render() {
    return (
      <div style={{ position: 'relative' }}>
        <TaskList tasks={this.state.tasks} />
        {this.renderLoadMore()}
      </div>
    );
  }
}

PendingTaskContainer.propTypes = {
  languageCode: React.PropTypes.string.isRequired,
  tasks: React.PropTypes.array.isRequired,
  total: React.PropTypes.number.isRequired,
};


export default PendingTaskContainer;
