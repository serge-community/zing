/*
 * Copyright (C) Pootle contributors.
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React, { PropTypes } from 'react';
import { PureRenderMixin } from 'react-addons-pure-render-mixin';

import Avatar from 'components/Avatar';
import TimeSince from 'components/TimeSince';
import { tct } from 'utils/i18n';

const Check = ({ name, displayName }) => (
  <a href={`#${name}`}>{displayName}</a>
);
Check.propTypes = {
  name: PropTypes.string.isRequired,
  displayName: PropTypes.string.isRequired,
};

const SourceString = ({ sourceText, url }) => (
  <i><a href={url}>{sourceText}</a></i>
);
SourceString.propTypes = {
  sourceText: PropTypes.string.isRequired,
  url: PropTypes.string.isRequired,
};

const UserEvent = React.createClass({

  propTypes: {
    displayName: PropTypes.string,
    email: PropTypes.string.isRequired,
    timestamp: PropTypes.number,
    type: PropTypes.number.isRequired,
    unitSource: PropTypes.string.isRequired,
    unitUrl: PropTypes.string.isRequired,

    checkName: PropTypes.string,
    checkDisplayName: PropTypes.string,
    translationActionType: PropTypes.number,
    username: PropTypes.string.isRequired,
  },

  mixins: [PureRenderMixin],

  getActionText(user) {
    const { checkName } = this.props;
    const { checkDisplayName } = this.props;
    const { translationActionType } = this.props;
    const { type } = this.props;
    const { unitSource } = this.props;
    const { unitUrl } = this.props;

    const sourceString = (
      <SourceString
        url={unitUrl}
        sourceText={unitSource}
      />
    );

    let check;
    if (checkName !== undefined && checkDisplayName !== undefined) {
      check = (
        <Check
          name={checkName}
          displayName={checkDisplayName}
        />
      );
    }

    const NORMAL = 1;       // Regular edit via web UI
    const REVERT = 2;       // Revert action via web UI
    const SUGG_ACCEPT = 3;  // Accept a suggestion
    const UPLOAD = 4;       // Upload an offline file
    const SYSTEM = 5;       // Batch actions performed offline
    const MUTE_CHECK = 6;   // Mute quality check
    const UNMUTE_CHECK = 7; // Unmute quality check
    const SUGG_ADD = 8;     // Add new suggestion
    const SUGG_REJECT = 9;  // Reject suggestion

    // Translation action types:
    const TRANSLATED = 0;
    const EDITED = 1;
    const PRE_TRANSLATED = 2;
    const REMOVED = 3;
    const REVIEWED = 4;
    const NEEDS_WORK = 5;

    if (type === REVERT) {
      return tct('%(user)s removed translation for %(sourceString)s', { user, sourceString });
    } else if (type === SUGG_ACCEPT) {
      return tct('%(user)s accepted suggestion for %(sourceString)s', { user, sourceString });
    } else if (type === UPLOAD) {
      return tct('%(user)s uploaded file', { user });
    } else if (type === MUTE_CHECK) {
      return tct('%(user)s muted %(check)s for %(sourceString)s', { user, check, sourceString });
    } else if (type === UNMUTE_CHECK) {
      return tct('%(user)s unmuted %(check)s for %(sourceString)s', { user, check, sourceString });
    } else if (type === SUGG_ADD) {
      return tct('%(user)s added suggestion for %(sourceString)s', { user, sourceString });
    } else if (type === SUGG_REJECT) {
      return tct('%(user)s rejected suggestion for %(sourceString)s', { user, sourceString });
    } else if (type === NORMAL || type === SYSTEM) {
      if (translationActionType === TRANSLATED) {
        return tct('%(user)s translated %(sourceString)s', { user, sourceString });
      } else if (translationActionType === EDITED) {
        return tct('%(user)s edited %(sourceString)s', { user, sourceString });
      } else if (translationActionType === PRE_TRANSLATED) {
        return tct('%(user)s pre-translated %(sourceString)s', { user, sourceString });
      } else if (translationActionType === REMOVED) {
        return tct('%(user)s removed translation for %(sourceString)s', { user, sourceString });
      } else if (translationActionType === REVIEWED) {
        return tct('%(user)s reviewed %(sourceString)s', { user, sourceString });
      } else if (translationActionType === NEEDS_WORK) {
        return tct('%(user)s marked as needs work %(sourceString)s', { user, sourceString });
      }
    }

    return [user];
  },

  render() {
    const avatar = (
      <Avatar
        email={this.props.email}
        label={this.props.displayName || this.props.username}
        size={20}
        username={this.props.username}
      />
    );

    return (
      <div className="last-action">
        <span className="short-action-text">
          {avatar}
        </span>
        <span className="action-text">
          {this.getActionText(avatar)}
        </span>
        {' '}
        <TimeSince
          timestamp={this.props.timestamp}
        />
      </div>
    );
  },

});


export default UserEvent;
