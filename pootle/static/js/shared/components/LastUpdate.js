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
import _ from 'underscore';

import TimeSince from 'components/TimeSince';


const LastUpdate = React.createClass({

  propTypes: {
    timestamp: PropTypes.number.isRequired,
    unitSource: PropTypes.string.isRequired,
    unitUrl: PropTypes.string.isRequired,
  },

  mixins: [PureRenderMixin],

  getActionText() {
    const { unitSource } = this.props;
    const { unitUrl } = this.props;

    return {
      __html: `<i><a href="${unitUrl}">${_.escape(unitSource)}</a></i>`,
    };
  },

  render() {
    return (
      <div className="last-action">
        <TimeSince
          timestamp={this.props.timestamp}
        />{' '}
        <span
          className="action-text"
          dangerouslySetInnerHTML={this.getActionText()}
        />
      </div>
    );
  },

});


export default LastUpdate;
