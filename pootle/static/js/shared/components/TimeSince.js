/*
 * Copyright (C) Pootle contributors.
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React, { PropTypes } from 'react';

import { formatTimeDelta } from 'utils/time';

const TimeSince = React.createClass({
  propTypes: {
    timestamp: PropTypes.number,
  },

  componentWillMount() {
    this.tickTimer = null;

    this.tick({ refresh: false });
  },

  componentWillReceiveProps(nextProps) {
    if (nextProps.timestamp !== this.props.timestamp) {
      this.cleanup();
    }
  },

  componentWillUnmount() {
    this.cleanup();
  },

  cleanup() {
    if (this.tickTimer !== null) {
      clearTimeout(this.tickTimer);
      this.tickTimer = null;
    }
  },

  tick(opts = { refresh: true }) {
    const past = new Date(this.props.timestamp * 1000);
    const now = Date.now();
    const seconds = Math.round(Math.abs(now - past) / 1000);

    let interval;

    if (seconds < 60) {
      interval = 1000 * 30;
    } else if (seconds < 60 * 60) {
      interval = 1000 * 60;
    } else if (seconds < 60 * 60 * 24) {
      interval = 1000 * 60 * 60;
    }

    if (interval !== undefined) {
      this.tickTimer = setTimeout(() => this.tick(), interval);
    }

    if (opts.refresh) {
      this.forceUpdate();
    }
  },

  render() {
    if (!this.props.timestamp) {
      return null;
    }

    const msEpoch = this.props.timestamp * 1000;
    const d = new Date(msEpoch);

    return (
      <time
        className="extra-item-meta"
        title={d.toUTCString()}
        dateTime={d.toUTCString()}
        {...this.props}
      >
        {formatTimeDelta(msEpoch, { addDirection: true })}
      </time>
    );
  },
});

export default TimeSince;
