/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';

const ColoredNumber = React.createClass({
  propTypes: {
    n: React.PropTypes.number,
  },

  render() {
    if (!this.props.n) {
      return (<span className="zero">0</span>);
    }
    return (
      <span>{this.props.n}</span>
    );
  },
});

export default ColoredNumber;
