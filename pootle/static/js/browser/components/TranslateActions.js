/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';

import { t } from 'utils/i18n';
import { getTranslateUrl } from 'utils/url';

import NumberPill from './NumberPill';

const Action = ({ caption, count, name, url }) => {
  const WrapperTag = url
    ? ({ children }) => (
        <a className={name} href={url}>
          {children}
        </a>
      )
    : ({ children }) => <span className={name}>{children}</span>;
  return (
    <WrapperTag>
      <span className="caption">{caption}</span> <NumberPill n={count} />
    </WrapperTag>
  );
};
Action.propTypes = {
  caption: React.PropTypes.string.isRequired,
  count: React.PropTypes.number.isRequired,
  name: React.PropTypes.string.isRequired,
  url: React.PropTypes.string,
};

const TranslateActions = ({ areActionsEnabled, pootlePath, stats }) => {
  const { critical, suggestions, total, translated } = stats;
  return (
    <ul>
      {critical > 0 && (
        <li>
          <Action
            name="fix-errors"
            caption={
              areActionsEnabled ? t('Fix critical errors') : t('Critical errors')
            }
            count={critical}
            url={
              areActionsEnabled
                ? getTranslateUrl(pootlePath, { category: 'critical' })
                : ''
            }
          />
        </li>
      )}
      {suggestions > 0 && (
        <li>
          <Action
            name="review-suggestions"
            caption={areActionsEnabled ? t('Review suggestions') : t('Suggestions')}
            count={suggestions}
            url={
              areActionsEnabled
                ? getTranslateUrl(pootlePath, { filter: 'suggestions' })
                : ''
            }
          />
        </li>
      )}
      {total - translated > 0 && (
        <li>
          <Action
            name="continue-translation"
            caption={
              areActionsEnabled ? t('Continue translation') : t('Incomplete')
            }
            count={total - translated}
            url={
              areActionsEnabled
                ? getTranslateUrl(pootlePath, { filter: 'incomplete' })
                : ''
            }
          />
        </li>
      )}
      {total > 0 && (
        <li>
          <Action
            name="translation-complete"
            caption={areActionsEnabled ? t('View all') : t('All')}
            count={total}
            url={areActionsEnabled ? getTranslateUrl(pootlePath) : ''}
          />
        </li>
      )}
    </ul>
  );
};
TranslateActions.propTypes = {
  canAdminDueDates: React.PropTypes.bool,
  initialDueDate: React.PropTypes.shape({
    id: React.PropTypes.number,
    due_on: React.PropTypes.number,
    pootle_path: React.PropTypes.string,
  }),
  areActionsEnabled: React.PropTypes.bool,
  pootlePath: React.PropTypes.string.isRequired,
  stats: React.PropTypes.shape({
    critical: React.PropTypes.number,
    suggestions: React.PropTypes.number,
    total: React.PropTypes.number.isRequired,
    translated: React.PropTypes.number.isRequired,
  }),
};

export default TranslateActions;
