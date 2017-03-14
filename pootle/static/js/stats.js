/*
 * Copyright (C) Pootle contributors.
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import $ from 'jquery';
import React from 'react';
import ReactDOM from 'react-dom';

import 'jquery-utils';
import assign from 'object-assign';

import StatsAPI from 'api/StatsAPI';
import LastActivity from 'components/LastActivity';
import TimeSince from 'components/TimeSince';
import { q } from 'utils/dom';
import { toLocaleString } from 'utils/i18n';

import BrowserTable from './browser/components/BrowserTable';
import FailingChecks from './browser/components/FailingChecks';
import PendingTaskContainer from './browser/components/PendingTaskContainer';
import Stats from './browser/components/Stats';
import StatsCollapsed from './browser/components/StatsCollapsed';
import TranslationState from './browser/components/TranslationState';


function formattedValue(n) {
  return n ? toLocaleString(n) : 0;
}

function nicePercentage(part, total, noTotalDefault) {
  const percentage = total ? part / total * 100 : noTotalDefault;
  if (percentage > 99 && percentage < 100) {
    return 99;
  }
  if (percentage > 0 && percentage < 1) {
    return 1;
  }
  return percentage > 0 ? Math.round(percentage) : 0;
}


function setTdWidth($td, w) {
  if (w === 0) {
    $td.hide();
  } else {
    $td.css('width', `${w}%`).show();
  }
}

function provideStatsDefaults(stats) {
  if (!stats.hasOwnProperty('children')) {
    return stats;
  }

  const newStats = assign({}, stats);
  newStats.children = [];
  Object.keys(stats.children).forEach((key) => {
    const item = stats.children[key];

    item.pootle_path = key;

    item.treeitem_type = item.treeitem_type || 0;
    item.critical = item.critical || 0;
    item.suggestions = item.suggestions || 0;
    item.lastaction = item.lastaction || {};
    item.lastaction.mtime = item.lastaction.mtime || 0;
    item.lastupdated = item.lastupdated || 0;

    item.total = item.total || 0;
    item.translated = item.translated || 0;
    item.progress = item.total > 0 ? item.translated / item.total : 1;
    item.incomplete = item.total - item.translated;

    newStats.children.push(item);
  });
  return newStats;
}


const stats = {

  init(options) {
    this.retries = 0;
    const isExpanded = (options.isInitiallyExpanded ||
                        window.location.search.indexOf('?details') !== -1);
    this.state = {
      isExpanded,
      checksData: null,
    };

    this.languageCode = options.languageCode;
    this.pootlePath = options.pootlePath;
    this.canTranslateStats = options.canTranslateStats;
    this.isAdmin = options.isAdmin;
    this.statsRefreshAttemptsCount = options.statsRefreshAttemptsCount;

    this.$extraDetails = $('#js-path-summary-more');
    this.$expandIcon = $('#js-expand-icon');

    $(document).on('click', '#js-path-summary', (e) => {
      e.preventDefault();
      this.toggleDetailedStats();
    });
    $(document).on('click', '.js-stats-refresh', (e) => {
      e.preventDefault();
      this.refreshStats();
    });
    $(document).on('click', '.js-stats-refresh-close', (e) => {
      e.preventDefault();
      $('#autorefresh-notice').hide();
    });

    window.addEventListener('popstate', (e) => {
      const state = e.state;
      if (state) {
        this.setState({ isExpanded: state.isExpanded });
      }
    });

    if (options.pendingTasks) {
      this.setTasks(options.pendingTasks.items, options.pendingTasks.total);
    }

    ReactDOM.render(
      <StatsCollapsed
        topContributors={options.topContributorsData.items}
      />,
      q('#js-path-summary-collapsed')
    );

    ReactDOM.render(
      <Stats
        hasMoreContributors={options.topContributorsData.has_more_items}
        topContributors={options.topContributorsData.items}
        pootlePath={this.pootlePath}
      />,
      q('#js-mnt-top-contributors')
    );

    this.setState({
      data: options.initialData,
    });

    // Retrieve async data if needed
    if (isExpanded) {
      this.loadChecks();
    }
  },

  setState(newState) {
    this.state = assign(
      {}, this.state, newState,
      newState.hasOwnProperty('data') ?
        { data: provideStatsDefaults(newState.data) } :
        {}
    );
    this.updateUI();
  },

  setTasks(tasks, total) {
    this.taskContainer = ReactDOM.render(
      <PendingTaskContainer
        languageCode={this.languageCode}
        initialTasks={tasks}
        initialTotal={total}
      />,
      q('.js-mnt-pending-tasks')
    );
  },

  refreshTasks() {
    // FIXME: don't access component's internals like this. Move state up ASAP.
    this.taskContainer.handleRefresh();
  },

  refreshStats() {
    this.dirtyBackoff = 1;
    this.updateDirty();
  },

  updateProgressbar($td, item) {
    const translated = nicePercentage(item.translated, item.total, 100);
    const fuzzy = nicePercentage(item.fuzzy, item.total, 0);
    const untranslatedCount = 100 - translated - fuzzy;
    const untranslated = untranslatedCount < 0 ? 0 : untranslatedCount;
    const $legend = $('<span>').html($td.find('script').text());

    $legend.find('.value.translated').text(translated);
    $legend.find('.value.fuzzy').text(fuzzy);
    $legend.find('.value.untranslated').text(untranslated);

    $td.find('table').attr('title', $legend.html());

    setTdWidth($td.find('td.translated'), translated);
    setTdWidth($td.find('td.fuzzy'), fuzzy);
    setTdWidth($td.find('td.untranslated'), untranslated);
  },

  updateAction($action, count) {
    $action.toggleClass('non-zero', count > 0);
    $action.find('.counter').text(formattedValue(count));
  },

  renderLastEvent(el, data) {
    if (data.mtime === 0) {
      return false;
    }
    ReactDOM.render(<LastActivity {...data} />, el);
    return true;
  },

  renderLastUpdate(el, timestamp) {
    if (timestamp === 0) {
      return false;
    }

    ReactDOM.render(<TimeSince timestamp={timestamp} />, el);
    return true;
  },

  updateLastUpdates(statsData) {
    const luWrapper = q('#js-last-updated-wrapper');
    const hideLastUpdated = !statsData.lastupdated || statsData.lastupdated.mtime === 0;
    luWrapper.classList.toggle('hide', hideLastUpdated);
    if (statsData.lastupdated) {
      const lastUpdated = q('#js-last-updated');
      this.renderLastUpdate(lastUpdated, statsData.lastupdated);
    }
    const laWrapper = q('#js-last-action-wrapper');
    const hideLastAction = !statsData.lastaction || statsData.lastaction.mtime === 0;
    laWrapper.classList.toggle('hide', hideLastAction);
    if (statsData.lastaction) {
      const lastAction = q('#js-last-action');
      this.renderLastEvent(lastAction, statsData.lastaction);
    }
  },

  updateStatsUI() {
    const { data } = this.state;

    const dirtySelector = '#top-stats, #translate-actions, #autorefresh-notice';
    const dirtyStatsRefreshEnabled = this.retries < this.statsRefreshAttemptsCount;

    $(dirtySelector).toggleClass('dirty', !!data.is_dirty && !dirtyStatsRefreshEnabled);
    if (!!data.is_dirty) {
      if (dirtyStatsRefreshEnabled) {
        this.dirtyBackoff = Math.pow(2, this.retries);
        this.dirtyBackoffId = setInterval(() => this.updateDirty({ hideSpin: true }), 1000);
      } else {
        $('.js-stats-refresh').show();
      }
    }

    this.updateProgressbar($('#progressbar'), data);
    this.updateAction($('#js-action-view-all'), data.total);
    this.updateAction($('#js-action-continue'), data.total - data.translated);
    this.updateAction($('#js-action-fix-critical'), data.critical);
    this.updateAction($('#js-action-review'), data.suggestions);

    ReactDOM.render(
      <TranslationState
        total={data.total}
        translated={data.translated}
        fuzzy={data.fuzzy}
        canTranslate={this.canTranslateStats}
        pootlePath={this.pootlePath}
      />,
      q('.js-mnt-translation-state')
    );
    this.updateLastUpdates(data);
  },

  updateDirty({ hideSpin = false } = {}) {
    if (--this.dirtyBackoff === 0) {
      $('.js-stats-refresh').hide();
      clearInterval(this.dirtyBackoffId);
      setTimeout(() => {
        if (this.retries < 5) {
          this.retries++;
        }
        this.loadStats({ hideSpin });
      }, 250);
    }
  },

  load(methodName, { hideSpin = false } = {}) {
    if (!hideSpin) {
      $('body').spin();
    }
    return StatsAPI[methodName](this.pootlePath)
      .always(() => $('body').spin(false));
  },

  loadStats({ hideSpin = false } = {}) {
    return this.load('getStats', { hideSpin })
      .done((data) => this.setState({ data }));
  },

  loadChecks() {
    return this.load('getChecks')
      .done((data) => this.setState({ isExpanded: true, checksData: data }));
  },

  /* Path summary */
  toggleDetailedStats() {
    if (this.state.checksData) {
      this.setState({ isExpanded: !this.state.isExpanded });
      this.navigate();
    } else {
      this.loadChecks().done(() => this.navigate());
    }
  },

  updateChecksToggleUI() {
    const { isExpanded } = this.state;

    const newClass = isExpanded ? 'collapse' : 'expand';
    const newText = isExpanded ? gettext('Collapse details') : gettext('Expand details');

    this.$expandIcon.attr('class', `icon-${newClass}-stats`);
    this.$expandIcon.attr('title', newText);

    this.$extraDetails.toggleClass('expand', isExpanded);
  },

  updateChecksUI() {
    if (!this.state.checksData) {
      return;
    }

    // FIXME: load component on-demand
    ReactDOM.render(
      <FailingChecks
        canTranslate={this.canTranslateStats}
        items={this.state.checksData}
        pootlePath={this.pootlePath}
      />,
      q('.js-mnt-failing-checks')
    );
  },

  updateTableUI() {
    ReactDOM.render(
      <BrowserTable
        items={this.state.data.children}
      />,
      q('#js-browsing-table-container')
    );
  },

  updateUI() {
    this.updateChecksToggleUI();
    this.updateChecksUI();
    this.updateStatsUI();
    this.updateTableUI();
  },

  navigate() {
    const { isExpanded } = this.state;
    const currentURL = `${window.location.pathname}${window.location.search}`;
    const newURL = isExpanded ? `${this.pootlePath}?details` : this.pootlePath;
    if (currentURL !== newURL) {
      window.history.pushState({ isExpanded }, '', newURL);
    }
  },

};


export default stats;
