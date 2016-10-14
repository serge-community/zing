/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';

const ProgressBar = React.createClass({
  propTypes: {
    total: React.PropTypes.number,
    fuzzy: React.PropTypes.number,
    translated: React.PropTypes.number,
  },

  getDefaultProps() {
    return {
      total: 0,
      fuzzy: 0,
      translated: 0,
    };
  },

  render() {
    const { total, fuzzy, translated } = this.props;
    const pTrans = `${total > 0 ? Math.round(trans / total * 100) : 100}%`;
    const pFuzzy = `${total > 0 ? Math.round(fuzzy / total * 100) : 0}%`;
    const pUntrans = `${100 - pTrans - pFuzzy}%`;

    const title = `<span class="legend translated"></span>
      <span class="value translated">${pTrans}</span> translated<br/>
      <span class="legend fuzzy"></span>
      <span class="value fuzzy">${pFuzzy}</span> needs work<br/>
      <span class="legend untranslated"></span>
      <span class="value untranslated">${pUntrans}</span> untranslated`;

    return (
      <table className="graph" title={title}>
        <tbody>
        <tr>
          <td className="translated" style={ { width: pTrans } }><span></span></td>
          <td className="fuzzy" style={ { width: pFuzzy } }><span></span></td>
          <td className="untranslated"><span></span></td>
        </tr>
        </tbody>
      </table>
    );
  },
});

export default ProgressBar;
