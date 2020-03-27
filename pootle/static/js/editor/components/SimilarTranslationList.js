/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';

import { t } from 'utils/i18n';

import SimilarTranslation from './SimilarTranslation';

const SimilarTranslationList = ({
  originalSource,
  results,
  sourceLang,
  targetLang,
}) => (
  <div id="tm-results" className="tm-server">
    <div className="extra-item-title">{t('Similar translations')}</div>
    {results.map((result, i) => (
      <SimilarTranslation
        key={i}
        originalSource={originalSource}
        result={result}
        sourceLang={sourceLang}
        targetLang={targetLang}
      />
    ))}
  </div>
);

SimilarTranslationList.propTypes = {
  originalSource: React.PropTypes.string.isRequired,
  results: React.PropTypes.array.isRequired,
  sourceLang: React.PropTypes.string.isRequired,
  targetLang: React.PropTypes.string.isRequired,
};

export default SimilarTranslationList;
