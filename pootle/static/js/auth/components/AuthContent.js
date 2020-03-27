/*
 * Copyright (C) Pootle contributors.
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Pootle project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';

const AuthContent = React.createClass({
  propTypes: {
    children: React.PropTypes.node,
    style: React.PropTypes.object,
  },

  render() {
    // FIXME: use flexbox when possible
    const outer = Object.assign(
      {
        display: 'table',
        height: '22em',
        width: '100%',
      },
      this.props.style
    );
    const style = {
      outer,
      inner: {
        display: 'table-cell',
        verticalAlign: 'middle',
      },
    };

    return (
      <div style={style.outer}>
        <div style={style.inner}>{this.props.children}</div>
      </div>
    );
  },
});

export default AuthContent;
