/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';


const PlurrHelp = React.createClass({

  propTypes: {
    style: React.PropTypes.object,
  },

  contextTypes: {
    currentLocaleDir: React.PropTypes.string,
  },

  render() {
    const style = {
      float: this.context.currentLocaleDir === 'rtl' ? 'left' : 'right',
      margin: '0.5em',
      fontSize: '70%',
      color: '#bbb',
    };

    return (
      <div style={style}>
        Live Plurr preview&nbsp;
        <a
          href="/pages/help/plurr/"
          target="_blank"
          title="Show help on Plurr format (in a new tab)"
        >(?)</a>
      </div>
    );
  },

});


export default PlurrHelp;
