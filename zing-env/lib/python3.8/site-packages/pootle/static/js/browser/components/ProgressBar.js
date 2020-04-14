/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';

import { t } from 'utils/i18n';

import { nicePercentage } from '../utils';


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
    const untranslated = total - translated - fuzzy;

    const pTransNumber = nicePercentage(translated, total, 100);
    const pFuzzyNumber = nicePercentage(fuzzy, total, 0);
    const pUntransNumber = nicePercentage(untranslated, total, 0);

    const titleParts = [];
    if (pTransNumber > 0) {
      titleParts.push(
        t('%(percent)s translated', {
          percent: '<span class="legend translated"></span>' +
            `<span class="value translated">${pTransNumber}%</span>`,
        })
      );
    }

    if (pFuzzyNumber > 0) {
      titleParts.push(
        t('%(percent)s needs work', {
          percent: '<span class="legend fuzzy"></span>' +
            `<span class="value fuzzy">${pFuzzyNumber}%</span>`,
        })
      );
    }

    if (pUntransNumber > 0) {
      titleParts.push(
        t('%(percent)s untranslated', {
          percent: '<span class="legend untranslated"></span>' +
            `<span class="value untranslated">${pUntransNumber}%</span>`,
        })
      );
    }

    return (
      <table className="graph" title={titleParts.join('<br />')}>
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
