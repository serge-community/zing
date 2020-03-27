/*
 * Copyright (C) Pootle contributors.
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';

import Modal from 'components/Modal';

import UserProfileForm from './UserProfileForm';

const UserProfileEdit = React.createClass({
  propTypes: {
    appRoot: React.PropTypes.string.isRequired,
    user: React.PropTypes.object.isRequired,
  },

  /* Lifecycle */

  getInitialState() {
    return {
      editing: /\/edit\/?$/.test(window.location),
    };
  },

  componentWillUpdate(nextProps, nextState) {
    this.handleURL(nextState);
  },

  /* State-changing handlers */

  handleEdit() {
    this.setState({ editing: true });
  },

  handleClose() {
    this.setState({
      editing: false,
    });
  },

  handleSave() {
    this.handleClose();
    window.location.reload();
  },

  handleURL(newState) {
    const { appRoot } = this.props;
    const newURL = newState.editing ? `${appRoot}edit/` : appRoot;
    window.history.pushState({}, '', newURL);
  },

  /* Layout */

  render() {
    return (
      <div>
        <div className="edit-profile-btn">
          <button className="btn btn-primary" onClick={this.handleEdit}>
            {gettext('Edit My Public Profile')}
          </button>
        </div>
        {this.state.editing && (
          <Modal
            className="user-edit"
            onClose={this.handleClose}
            title={gettext('My Public Profile')}
          >
            <div id="user-edit">
              <UserProfileForm user={this.props.user} onSuccess={this.handleSave} />
            </div>
          </Modal>
        )}
      </div>
    );
  },
});

export default UserProfileEdit;
