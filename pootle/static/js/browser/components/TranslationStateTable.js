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

const TranslationStateRow = ({ count, label, canTranslate, percent, url }) => (
  <tr>
    <td id="stats-name">{label}</td>
    <td className="stats-number">
      {canTranslate ? (
        <a className="stats-data" href={url}>
          {toLocaleString(count)}
        </a>
      ) : (
        <span className="stats-data">{toLocaleString(count)}</span>
      )}
    </td>
    <td className="stats-percentage">
      <span>{t('%(percent)s%', { percent })}</span>
    </td>
  </tr>
);
TranslationStateRow.propTypes = {
  count: React.PropTypes.number.isRequired,
  canTranslate: React.PropTypes.bool.isRequired,
  label: React.PropTypes.string.isRequired,
  percent: React.PropTypes.number.isRequired,
  url: React.PropTypes.string,
};

const TranslationStateTable = ({
  areDisabledItemsShown,
  total,
  translated,
  untranslated,
  fuzzy,
  canTranslate,
  pootlePath,
}) => (
  <table className="stats">
    <tbody>
      <TranslationStateRow
        label={t('Total')}
        count={total}
        canTranslate={canTranslate}
        percent={nicePercentage(total, total, 100)}
        url={getTranslateUrl(pootlePath, {
          includeDisabled: areDisabledItemsShown,
        })}
      />
      <TranslationStateRow
        label={t('Translated')}
        count={translated}
        canTranslate={canTranslate}
        percent={nicePercentage(translated, total, 100)}
        url={getTranslateUrl(pootlePath, {
          filter: 'translated',
          includeDisabled: areDisabledItemsShown,
        })}
      />
      <TranslationStateRow
        label={t('Fuzzy')}
        count={fuzzy}
        canTranslate={canTranslate}
        percent={nicePercentage(fuzzy, total, 0)}
        url={getTranslateUrl(pootlePath, {
          filter: 'fuzzy',
          includeDisabled: areDisabledItemsShown,
        })}
      />
      <TranslationStateRow
        label={t('Untranslated')}
        count={untranslated}
        canTranslate={canTranslate}
        percent={nicePercentage(untranslated, total, 0)}
        url={getTranslateUrl(pootlePath, {
          filter: 'untranslated',
          includeDisabled: areDisabledItemsShown,
        })}
      />
    </tbody>
  </table>
);
TranslationStateTable.propTypes = {
  areDisabledItemsShown: React.PropTypes.bool.isRequired,
  total: React.PropTypes.number.isRequired,
  translated: React.PropTypes.number.isRequired,
  untranslated: React.PropTypes.number.isRequired,
  fuzzy: React.PropTypes.number.isRequired,
  canTranslate: React.PropTypes.bool.isRequired,
  pootlePath: React.PropTypes.string.isRequired,
};

export default TranslationStateTable;
