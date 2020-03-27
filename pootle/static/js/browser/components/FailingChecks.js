/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';

import { t } from 'utils/i18n';

import FailingChecksTable from './FailingChecksTable';

const DISPLAY_ITEMS_STEP = 5;

class FailingChecks extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      displayItemsCount: DISPLAY_ITEMS_STEP,
    };
  }

  handleClick(e) {
    e.preventDefault();
    this.setState((prevState) => ({
      displayItemsCount: prevState.displayItemsCount + DISPLAY_ITEMS_STEP,
    }));
  }

  render() {
    const { canTranslate } = this.props;
    const { pootlePath } = this.props;
    const { displayItemsCount } = this.state;
    const displayItems = this.props.items.slice(0, displayItemsCount);

    return (
      <div className="stats-checks">
        <h3>{t('Failing Checks')}</h3>
        <div className="bd">
          <FailingChecksTable
            canTranslate={canTranslate}
            items={displayItems}
            pootlePath={pootlePath}
          />
          {displayItemsCount < this.props.items.length && (
            <div className="toggle-more-checks">
              <a href="#" onClick={(e) => this.handleClick(e)}>
                {t('More...')}
              </a>
            </div>
          )}
        </div>
      </div>
    );
  }
}
FailingChecks.propTypes = {
  items: React.PropTypes.array.isRequired,
  canTranslate: React.PropTypes.bool.isRequired,
  pootlePath: React.PropTypes.string.isRequired,
};

export default FailingChecks;
