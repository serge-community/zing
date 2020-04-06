/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';

import LastActivity from 'components/LastActivity';
import TimeSince from 'components/TimeSince';

import FailingChecks from './FailingChecks';
import TopContributors from './TopContributors';
import TranslationStateTable from './TranslationStateTable';

import { t } from 'utils/i18n';

const DetailedStats = ({
  areDisabledItemsShown,
  canTranslate,
  failingChecksData,
  stats,
  pootlePath,
  hasMoreContributors,
  topContributorsData,
}) => {
  const lastUpdated = stats.lastupdated;
  const lastAction = stats.lastaction;
  const { total, translated, fuzzy } = stats;

  return (
    <div>
      <div className="summary-1-col">
        <h3 className="top">{t('Translation Statistics')}</h3>
        <div className="bd">
          <TranslationStateTable
            areDisabledItemsShown={areDisabledItemsShown}
            total={total}
            translated={translated}
            untranslated={total - translated - fuzzy}
            fuzzy={fuzzy}
            canTranslate={canTranslate}
            pootlePath={pootlePath}
          />
        </div>
        {failingChecksData && failingChecksData.length > 0 && (
          <FailingChecks
            areDisabledItemsShown={areDisabledItemsShown}
            canTranslate={canTranslate}
            items={failingChecksData}
            pootlePath={pootlePath}
          />
        )}
      </div>

      <div className="summary-2-col">
        <TopContributors
          hasMoreContributors={hasMoreContributors}
          topContributors={topContributorsData}
          pootlePath={pootlePath}
        />
      </div>

      {(lastAction || lastUpdated > 0) && (
        <div className="summary-3-col">
          {lastUpdated > 0 && (
            <div>
              <h3 className="top">{t('Updates')}</h3>
              <div className="bd">
                <div className="action-wrapper">
                  <label>{t('Last action:')}</label>{' '}
                  <div className="last-updated">
                    <TimeSince timestamp={lastUpdated} />
                  </div>
                </div>
              </div>
            </div>
          )}
          {lastAction && lastAction.mtime > 0 && (
            <div>
              <h3 className="top">{t('Translations')}</h3>
              <div className="bd">
                <div className="action-wrapper">
                  <label>{t('Last action:')}</label>{' '}
                  <div className="last-action">
                    <LastActivity {...lastAction} />
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      <div className="clear"></div>
    </div>
  );
};
DetailedStats.propTypes = {
  areDisabledItemsShown: React.PropTypes.bool.isRequired,
  canTranslate: React.PropTypes.bool.isRequired,
  failingChecksData: React.PropTypes.array,
  hasMoreContributors: React.PropTypes.bool,
  pootlePath: React.PropTypes.string.isRequired,
  stats: React.PropTypes.object.isRequired,
  topContributorsData: React.PropTypes.array,
};
DetailedStats.defaultProps = {
  failingChecksData: [],
  hasMoreContributors: false,
  topContributorsData: [],
};

export default DetailedStats;
