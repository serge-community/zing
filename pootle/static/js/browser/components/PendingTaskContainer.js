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


const REFRESH_MINUTES = 10;


class PendingTaskContainer extends React.Component {

  constructor(props) {
    super(props);

    this.state = {
      tasks: props.initialTasks,
      total: props.initialTotal,
    };
  }

  componentDidMount() {
    this.intervalId = setInterval(
      () => this.handleRefresh(), REFRESH_MINUTES * 60 * 1000
    );
  }

  componentWillReceiveProps(nextProps) {
    if (nextProps.hasOwnProperty('initialTasks') &&
        nextProps.hasOwnProperty('initialTotal')) {
      this.setState({
        tasks: nextProps.initialTasks,
        total: nextProps.initialTotal,
      });
    }
  }

  componentWillUnmount() {
    clearInterval(this.intervalId);
  }

  handleRefresh(opts = { extra: 0 }) {
    const limit = this.state.tasks.length + opts.extra;
    return TaskAPI.get(this.props.languageCode, { limit })
      .done((data) => {
        this.setState({ tasks: data.items, total: data.total });
      });
  }

  handleLoadMore(e) {
    e.preventDefault();
    return this.handleRefresh({ extra: 5 });
  }

  renderLoadMore() {
    const remaining = this.state.total - this.state.tasks.length;
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
        <TaskList
          canAdmin={this.props.canAdmin}
          tasks={this.state.tasks}
        />
        {this.renderLoadMore()}
      </div>
    );
  }
}

PendingTaskContainer.propTypes = {
  canAdmin: React.PropTypes.bool.isRequired,
  languageCode: React.PropTypes.string.isRequired,
  initialTasks: React.PropTypes.array.isRequired,
  initialTotal: React.PropTypes.number.isRequired,
};


export default PendingTaskContainer;
