/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';

import diff from 'utils/diff';
import { dir, t, tct } from 'utils/i18n';

import { highlightRO } from '../../utils';


const Result = ({ originalSource, source, sourceLang, target, targetLang }) => (
  <div className="suggestion-wrapper">
    <div
      className="suggestion-original"
      dangerouslySetInnerHTML={{ __html: diff(originalSource, source) }}
      dir={dir(sourceLang)}
      lang={sourceLang}
    />
    <div
      className="suggestion-translation"
      dir={dir(targetLang)}
      lang={targetLang}
    >
      {highlightRO(target)}
    </div>
  </div>
);

Result.propTypes = {
  originalSource: React.PropTypes.string.isRequired,
  source: React.PropTypes.string.isRequired,
  sourceLang: React.PropTypes.string.isRequired,
  target: React.PropTypes.string.isRequired,
  targetLang: React.PropTypes.string.isRequired,
};


const Context = ({
  displaySubmittedOn, fullname, isoSubmittedOn, path, project, username,
}) => {
  let name = fullname;
  if (username === 'nobody') {
    name = t('some anonymous user');
  } else if (!fullname) {
    name = username || t('someone');
  }

  const ctx = {
    name: <span>{name}</span>,
    path,
    project: <span title={path}>{project}</span>,
  };

  return (
    <div className="tm-context">
      {tct('Translated by %(name)s in %(project)s project', ctx)}
      <time
        className="extra-item-meta js-relative-date"
        title={displaySubmittedOn}
        dateTime={isoSubmittedOn}
      >&nbsp;</time>
    </div>
  );
};

Context.propTypes = {
  displaySubmittedOn: React.PropTypes.string.isRequired,
  username: React.PropTypes.string,
  fullname: React.PropTypes.string,
  isoSubmittedOn: React.PropTypes.string.isRequired,
  path: React.PropTypes.string.isRequired,
  project: React.PropTypes.string.isRequired,
};


// FIXME: implement `js-editor-copy-tm-text` functionality here
const SimilarTranslation = ({
  originalSource, result, sourceLang, targetLang,
}) => (
  <div
    className="extra-item-block js-editor-copy-tm-text"
    data-action="overwrite"
    data-translation-aid={result.target}
  >
    <div className="extra-item-content">
      <div className="extra-item">
        <Result
          originalSource={originalSource}
          source={result.source}
          sourceLang={sourceLang}
          target={result.target}
          targetLang={targetLang}
        />
        <Context
          displaySubmittedOn={result.display_submitted_on}
          fullname={result.fullname}
          isoSubmittedOn={result.iso_submitted_on}
          path={result.path}
          project={result.project}
          username={result.username}
        />
      </div>
    </div>
  </div>
);

SimilarTranslation.propTypes = {
  originalSource: React.PropTypes.string.isRequired,
  result: React.PropTypes.object.isRequired, // FIXME: make it flat
  sourceLang: React.PropTypes.string.isRequired,
  targetLang: React.PropTypes.string.isRequired,
};


export default SimilarTranslation;
