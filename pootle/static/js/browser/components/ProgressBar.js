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
    const pTransNumber = total > 0 ? Math.round(translated / total * 100) : 100;
    const pFuzzyNumber = total > 0 ? Math.round(fuzzy / total * 100) : 0;
    const pUntransNumber = 100 - pTransNumber - pFuzzyNumber;

    let title = '';
    if (pTransNumber > 0) {
      title = `${title}
        <span class="legend translated"></span>
        <span class="value translated">${pTransNumber}%</span> translated<br/>
      `;
    }
    if (pFuzzyNumber > 0) {
      title = `${title}
        <span class="legend fuzzy"></span>
        <span class="value fuzzy">${pFuzzyNumber}%</span> needs work<br/>
      `;
    }
    if (pUntransNumber > 0) {
      title = `${title}
        <span class="legend untranslated"></span>
        <span class="value untranslated">${pUntransNumber}%</span> untranslated
      `;
    }

    return (
      <table className="graph" title={title}>
        <tbody>
        <tr>
        {pTransNumber > 0 &&
          <td
            className="translated"
            style={{ width: `${pTransNumber}%` }}
          >
            <span></span>
          </td>
        }
        {pFuzzyNumber > 0 &&
          <td
            className="fuzzy"
            style={{ width: `${pFuzzyNumber}%` }}
          >
            <span></span>
          </td>
        }
        {pUntransNumber > 0 &&
          <td
            className="untranslated"
            style={{ width: `${pUntransNumber}%` }}
          >
            <span></span>
          </td>
        }
        </tr>
        </tbody>
      </table>
    );
  },
});

export default ProgressBar;
