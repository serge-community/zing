/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';

const NumberPill = React.createClass({
  propTypes: {
    n: React.PropTypes.number,
    url: React.PropTypes.string.isRequired,
  },

  render() {
    if (!this.props.n) {
      return (<span className="zero">0</span>);
    }
    return (
      <a className="stats-data" href={this.props.url}>{this.props.n}</a>
    );
  },
});

export default NumberPill;
