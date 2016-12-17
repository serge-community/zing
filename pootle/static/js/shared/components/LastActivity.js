/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';
import UserEvent from 'components/UserEvent';


const LastActivity = React.createClass({
  propTypes: {
    mtime: React.PropTypes.number,
    check: React.PropTypes.string,
    check_displayname: React.PropTypes.string,
    displayname: React.PropTypes.string,
    email: React.PropTypes.string,
    type: React.PropTypes.number,
    translation_action_type: React.PropTypes.number,
    source: React.PropTypes.string,
    uid: React.PropTypes.number,
    username: React.PropTypes.string,
  },

  render() {
    if (!this.props.mtime) {
      return null;
    }

    const props = {
      checkName: this.props.check,
      checkDisplayName: this.props.check_displayname,
      displayName: this.props.displayname,
      email: this.props.email || '',
      timestamp: this.props.mtime,
      type: this.props.type,
      translationActionType: this.props.translation_action_type || 0,
      unitSource: this.props.source,
      unitUrl: `/unit/${this.props.uid}`,
      username: this.props.username,
    };

    return <UserEvent {...props} />;
  },
});

export default LastActivity;
