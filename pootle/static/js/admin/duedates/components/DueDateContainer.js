/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';

import DueDateAPI from 'api/DueDateAPI';

import DueDateWidget from './DueDateWidget';


class DueDateContainer extends React.Component {

  constructor(props) {
    super(props);

    const { initialDueDate } = props;
    this.state = {
      id: initialDueDate.id,
      isOpen: false,
      dueOn: initialDueDate.due_on,
      pootlePath: initialDueDate.pootle_path,
    };
  }

  handleRemove(id) {
    DueDateAPI
      .remove(id)
      .then(() => this.setState({
        id: null,
        dueOn: 0,
      }, this.handlePostUpdate));
  }

  handleUpdate(isoDate) {
    const { id } = this.state;
    let promise;
    if (id) {
      promise = DueDateAPI.update(id, isoDate);
    } else {
      promise = DueDateAPI.add(this.state.pootlePath, isoDate);
    }
    promise.then((dueDate) => {
      this.setState(() => ({
        id: dueDate.id,
        dueOn: dueDate.due_on,
      }), this.handlePostUpdate);
    });
  }

  handlePostUpdate() {
    // FIXME: dirty but okayish for now
    PTL.stats.refreshTasks();
  }

  handleToggle() {
    this.setState((prevState) => ({
      isOpen: !prevState.isOpen,
    }));
  }

  render() {
    return (
      <DueDateWidget
        dueOn={this.state.dueOn}
        id={this.state.id}
        isOpen={this.state.isOpen}
        onRemove={(id) => this.handleRemove(id)}
        onToggle={() => this.handleToggle()}
        onUpdate={(isoDate) => this.handleUpdate(isoDate)}
      />
    );
  }

}

DueDateContainer.propTypes = {
  initialDueDate: React.PropTypes.shape({
    id: React.PropTypes.number,
    due_on: React.PropTypes.number,
    pootle_path: React.PropTypes.string,
  }),
};
DueDateContainer.defaultProps = {
  initialDueDate: {},
};


export default DueDateContainer;
