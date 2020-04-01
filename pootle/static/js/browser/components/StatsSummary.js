/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import cx from 'classnames';
import $ from 'jquery';
import React from 'react';

import StatsAPI from 'api/StatsAPI';

import DetailedStats from './DetailedStats';
import ProgressBar from './ProgressBar';
import TopContributorsList from './TopContributorsList';

class StatsSummary extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      isExpanded: props.isInitiallyExpanded,
      failingChecksData: null,
    };

    this.handlePopState = this.handlePopState.bind(this);
  }

  componentDidMount() {
    window.addEventListener('popstate', this.handlePopState);

    if (!this.state.isExpanded) {
      return;
    }

    this.loadChecks();
  }

  componentWillUnmount() {
    window.removeEventListener('popstate', this.handlePopState);
  }

  handlePopState(e) {
    if (e.state) {
      this.setState({ isExpanded: e.state.isExpanded });
    }
  }

  handleClick(e) {
    e.preventDefault();
    this.setState(
      (prevState) => ({
        isExpanded: !prevState.isExpanded,
      }),
      () => {
        this.navigate();
        this.loadChecks();
      }
    );
  }

  loadChecks() {
    if (this.state.failingChecksData) {
      return;
    }

    // FIXME: display spinners declaratively
    $('body').spin();
    StatsAPI.getChecks(this.props.pootlePath)
      .done((data) => this.setState({ failingChecksData: data }))
      .always(() => $('body').spin(false));
  }

  navigate() {
    const { isExpanded } = this.state;
    const { pootlePath } = this.props;
    const currentURL = `${window.location.pathname}${window.location.search}`;
    const newURL = isExpanded ? `${pootlePath}?details` : pootlePath;
    if (currentURL !== newURL) {
      window.history.pushState({ isExpanded }, '', newURL);
    }
  }

  render() {
    const { canTranslate } = this.props;
    const { stats } = this.props;
    const { pootlePath } = this.props;
    const { hasMoreContributors } = this.props;
    const { topContributorsData } = this.props;
    const { failingChecksData } = this.state;
    const { isExpanded } = this.state;

    const iconClasses = cx({
      'icon-collapse-stats': isExpanded,
      'icon-expand-stats': !isExpanded,
    });
    const wrapperClasses = cx({
      'path-summary-collapsed': !isExpanded,
    });

    // FIXME: import `<DetailedStats />` component on demand
    return (
      <div id="top-stats" className="header">
        <a href="#" onClick={(e) => this.handleClick(e)}>
          <div id="progressbar">
            <ProgressBar
              total={stats.total}
              fuzzy={stats.fuzzy}
              translated={stats.translated}
            />
          </div>
        </a>
        <div className="path-summary-more">
          <a className="expand-stats" href="#" onClick={(e) => this.handleClick(e)}>
            <i className={iconClasses}></i>
          </a>

          <div className={wrapperClasses}>
            {isExpanded ? (
              <DetailedStats
                canTranslate={canTranslate}
                failingChecksData={failingChecksData}
                hasMoreContributors={hasMoreContributors}
                pootlePath={pootlePath}
                stats={stats}
                topContributorsData={topContributorsData}
              />
            ) : (
              <TopContributorsList topContributors={topContributorsData} />
            )}
          </div>
        </div>
      </div>
    );
  }
}
StatsSummary.propTypes = {
  canTranslate: React.PropTypes.bool.isRequired,
  hasMoreContributors: React.PropTypes.bool,
  isInitiallyExpanded: React.PropTypes.bool.isRequired,
  pootlePath: React.PropTypes.string.isRequired,
  stats: React.PropTypes.object.isRequired,
  topContributorsData: React.PropTypes.array,
};
StatsSummary.defaultProps = {
  hasMoreContributors: false,
  topContributorsData: [],
};

export default StatsSummary;
