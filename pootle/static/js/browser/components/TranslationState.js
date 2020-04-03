/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';

import { t } from 'utils/i18n';

import TranslationStateTable from './TranslationStateTable';

const TranslationState = ({
  areDisabledItemsShown,
  total,
  translated,
  fuzzy,
  canTranslate,
  pootlePath,
}) => (
  <div>
    <h3 className="top">{t('Translation Statistics')}</h3>
    <div className="bd">
      <TranslationStateTable
        areDisabledItemsShown={areDisabledItemsShown}
        total={total}
        translated={translated}
        untranslated={total === null ? null : total - translated - fuzzy}
        fuzzy={fuzzy}
        canTranslate={canTranslate}
        pootlePath={pootlePath}
      />
    </div>
  </div>
);
TranslationState.propTypes = {
  areDisabledItemsShown: React.PropTypes.bool.isRequired,
  total: React.PropTypes.number.isRequired,
  translated: React.PropTypes.number,
  fuzzy: React.PropTypes.number,
  canTranslate: React.PropTypes.bool.isRequired,
  pootlePath: React.PropTypes.string.isRequired,
};
TranslationState.defaultProps = {
  fuzzy: 0,
  translated: 0,
};

export default TranslationState;
