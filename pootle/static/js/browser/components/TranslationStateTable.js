/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';

import { t, toLocaleString } from 'utils/i18n';
import { getTranslateUrl } from 'utils/url';

import { nicePercentage } from '../utils';


const TranslationStateRow = ({
  code, count, label, canTranslate, percent, pootlePath,
}) => (
  <tr>
    <td id="stats-name">{label}</td>
    <td className="stats-number">
    {canTranslate ?
      <a
        className="stats-data"
        href={getTranslateUrl(pootlePath, { filter: code !== 'total' ? code : null })}
      >
        {toLocaleString(count)}
      </a>
      :
      <span className="stats-data">{toLocaleString(count)}</span>
    }
    </td>
    <td className="stats-percentage">
      <span>{t('%(percent)s%', { percent })}</span>
    </td>
  </tr>
);
TranslationStateRow.propTypes = {
  code: React.PropTypes.string.isRequired,
  count: React.PropTypes.number.isRequired,
  canTranslate: React.PropTypes.bool.isRequired,
  label: React.PropTypes.string.isRequired,
  percent: React.PropTypes.number.isRequired,
  pootlePath: React.PropTypes.string.isRequired,
};


const TranslationStateTable = ({
  total, translated, untranslated, fuzzy, canTranslate, pootlePath,
}) => (
  <table className="stats">
    <tbody>
      <TranslationStateRow
        code="total"
        label={t('Total')}
        count={total}
        canTranslate={canTranslate}
        percent={nicePercentage(total, total, 100)}
        pootlePath={pootlePath}
      />
      <TranslationStateRow
        code="translated"
        label={t('Translated')}
        count={translated}
        canTranslate={canTranslate}
        percent={nicePercentage(translated, total, 100)}
        pootlePath={pootlePath}
      />
      <TranslationStateRow
        code="fuzzy"
        label={t('Fuzzy')}
        count={fuzzy}
        canTranslate={canTranslate}
        percent={nicePercentage(fuzzy, total, 0)}
        pootlePath={pootlePath}
      />
      <TranslationStateRow
        code="untranslated"
        label={t('Untranslated')}
        count={untranslated}
        canTranslate={canTranslate}
        percent={nicePercentage(untranslated, total, 0)}
        pootlePath={pootlePath}
      />
    </tbody>
  </table>
);
TranslationStateTable.propTypes = {
  total: React.PropTypes.number.isRequired,
  translated: React.PropTypes.number.isRequired,
  untranslated: React.PropTypes.number.isRequired,
  fuzzy: React.PropTypes.number.isRequired,
  canTranslate: React.PropTypes.bool.isRequired,
  pootlePath: React.PropTypes.string.isRequired,
};

export default TranslationStateTable;
