/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';

import { toLocaleString } from 'utils/i18n';

const NumberPill = React.createClass({
  propTypes: {
    n: React.PropTypes.number,
    url: React.PropTypes.string,
  },

  render() {
    if (!this.props.n) {
      return <span className="zero">0</span>;
    }

    if (!this.props.url) {
      return <span className="counter">{toLocaleString(this.props.n)}</span>;
    }

    return (
      <a className="counter" href={this.props.url}>
        {toLocaleString(this.props.n)}
      </a>
    );
  },
});

export default NumberPill;
