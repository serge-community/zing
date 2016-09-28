/*
 * Copyright (C) Pootle contributors.
 *
 * This file is a part of the Pootle project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';
import UserEvent from 'components/UserEvent';

const LastActivity = React.createClass({
    render: function() {
        if (!this.props.mtime) {
            return (<span />)
        }

        const props = {
            checkName:  this.props.check,
            checkDisplayName: this.props.check_displayname,
            displayName: this.props.displayname,
            email: this.props.email || '',
            timestamp: this.props.mtime,
            type: this.props.type,
            translationActionType: this.props.translation_action_type || 0,
            unitSource: this.props.source,
            unitUrl: '/unit/'+this.props.unit,
            username: this.props.username,
        };

        return (<UserEvent {...props} />);
    }
});

export default LastActivity;
