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

import StatsAPI from 'api/StatsAPI';
import { q } from 'utils/dom';
import { toLocaleString } from 'utils/i18n';

import BrowserTable from './browser/components/BrowserTable';
import StatsSummary from './browser/components/StatsSummary';
import PendingTaskContainer from './browser/components/PendingTaskContainer';


function formattedValue(n) {
  return n ? toLocaleString(n) : 0;
}

function provideStatsDefaults(stats) {
  if (!stats.hasOwnProperty('children')) {
    return stats;
  }

  const newStats = Object.assign({}, stats);
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
    this.isInitiallyExpanded = (
      options.isInitiallyExpanded ||
      window.location.search.indexOf('?details') !== -1
    );
    this.state = {};

    this.languageCode = options.languageCode;
    this.pootlePath = options.pootlePath;
    this.initialDueDate = options.dueDate;

    this.canAdminDueDates = options.canAdminDueDates;
    this.canTranslateStats = options.canTranslateStats;
    this.hasAdminAccess = options.hasAdminAccess;
    this.statsRefreshAttemptsCount = options.statsRefreshAttemptsCount;

    $(document).on('click', '.js-stats-refresh', (e) => {
      e.preventDefault();
      this.refreshStats();
    });
    $(document).on('click', '.js-stats-refresh-close', (e) => {
      e.preventDefault();
      $('#autorefresh-notice').hide();
    });

    if (options.pendingTasks) {
      this.setTasks(options.pendingTasks.items, options.pendingTasks.total);
    }

    this.setState({
      data: options.initialData,
      topContributorsData: options.topContributorsData,
    });
  },

  setState(newState) {
    this.state = Object.assign(
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
        canAdmin={this.hasAdminAccess}
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

  updateAction($action, count) {
    $action.toggleClass('non-zero', count > 0);
    $action.find('.counter').text(formattedValue(count));
  },

  updateStatsUI() {
    const { data } = this.state;

    const dirtySelector = '#top-stats, #translate-actions, #autorefresh-notice';
    const dirtyStatsRefreshEnabled = this.retries < this.statsRefreshAttemptsCount;

    $(dirtySelector).toggleClass('dirty', !!data.is_dirty && !dirtyStatsRefreshEnabled);
    if (!!data.is_dirty) {
      if (dirtyStatsRefreshEnabled) {
        this.dirtyBackoff = Math.pow(2, this.retries);
        this.dirtyBackoffId = setInterval(
          () => this.updateDirty({ showSpin: false }), 1000
        );
      } else {
        $('.js-stats-refresh').show();
      }
    }

    this.updateAction($('#js-action-view-all'), data.total);
    this.updateAction($('#js-action-continue'), data.total - data.translated);
    this.updateAction($('#js-action-fix-critical'), data.critical);
    this.updateAction($('#js-action-review'), data.suggestions);
  },

  updateDirty({ showSpin = true } = {}) {
    if (--this.dirtyBackoff === 0) {
      $('.js-stats-refresh').hide();
      clearInterval(this.dirtyBackoffId);
      setTimeout(() => {
        if (this.retries < 5) {
          this.retries++;
        }
        this.loadStats({ showSpin });
      }, 250);
    }
  },

  loadStats({ showSpin = true } = {}) {
    if (showSpin) {
      $('body').spin();
    }
    return StatsAPI
      .getStats(this.pootlePath)
      .done((data) => this.setState({ data }))
      .always(() => $('body').spin(false));
  },

  updateDueDatesAdminUI() {
    if (!this.canAdminDueDates) {
      return;
    }

    require.ensure([], () => {
      const DueDateContainer = (
        require('./admin/duedates/components/DueDateContainer').default
      );
      ReactDOM.render(
        <DueDateContainer initialDueDate={this.initialDueDate} />,
        q('.js-mnt-duedate-manage')
      );
    }, 'admin/duedates');
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
    this.updateStatsUI();

    ReactDOM.render(
      <StatsSummary
        isInitiallyExpanded={this.isInitiallyExpanded}
        canTranslate={this.canTranslateStats}
        hasMoreContributors={this.state.topContributorsData.has_more_items}
        pootlePath={this.pootlePath}
        statsData={this.state.data}
        topContributorsData={this.state.topContributorsData.items}
      />,
      q('.js-mnt-stats-summary')
    );

    this.updateDueDatesAdminUI();
    this.updateTableUI();
  },

};


export default stats;
