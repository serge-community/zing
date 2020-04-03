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

import BrowserTable from './browser/components/BrowserTable';
import StatsSummary from './browser/components/StatsSummary';
import PendingTaskContainer from './browser/components/PendingTaskContainer';
import ActionBar from './browser/components/ActionBar';

function getItem(item, path) {
  const newItem = {
    pootle_path: path,
    title: item.title || '',

    is_dirty: item.is_dirty || false,
    is_disabled: item.is_disabled || false,

    treeitem_type: item.treeitem_type || 0,
    critical: item.critical || 0,
    suggestions: item.suggestions || 0,
    lastaction: item.lastaction || {},
    lastupdated: item.lastupdated || 0,

    total: item.total || 0,
    translated: item.translated || 0,
    fuzzy: item.fuzzy || 0,
    progress: item.total > 0 ? item.translated / item.total : 1,
    incomplete: item.total - item.translated,
  };

  newItem.lastaction.mtime = newItem.lastaction.mtime || 0;

  return newItem;
}

function provideItemsDefaultStats(items) {
  return Object.keys(items).map((path) => getItem(items[path], path));
}

const stats = {
  init(options) {
    this.retries = 0;
    this.isInitiallyExpanded =
      options.isInitiallyExpanded ||
      window.location.search.indexOf('?details') !== -1;
    this.state = {};

    this.languageCode = options.languageCode;
    this.pootlePath = options.pootlePath;
    this.initialDueDate = options.dueDate;

    this.canAdminDueDates = options.canAdminDueDates;
    this.canTranslateStats = options.canTranslateStats;
    this.hasAdminAccess = options.hasAdminAccess;
    this.hasDisabledItems = options.hasDisabledItems;
    this.statsRefreshAttemptsCount = options.statsRefreshAttemptsCount;

    this.initialItem = getItem(options.initialData, options.pootlePath);
    this.fullItem = null;

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
      item: this.initialItem,
      items: options.initialData.children,
      topContributorsData: options.topContributorsData,
    });
  },

  setState(newState) {
    this.state = Object.assign(
      {},
      this.state,
      newState,
      newState.hasOwnProperty('items')
        ? { items: provideItemsDefaultStats(newState.items) }
        : {}
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

  updateStatsUI() {
    const { item } = this.state;

    const dirtySelector = '#top-stats, #translate-actions, #autorefresh-notice';
    const dirtyStatsRefreshEnabled = this.retries < this.statsRefreshAttemptsCount;

    $(dirtySelector).toggleClass(
      'dirty',
      !!item.is_dirty && !dirtyStatsRefreshEnabled
    );
    if (!!item.is_dirty) {
      if (dirtyStatsRefreshEnabled) {
        this.dirtyBackoff = Math.pow(2, this.retries);
        this.dirtyBackoffId = setInterval(
          () => this.updateDirty({ showSpin: false }),
          1000
        );
      } else {
        $('.js-stats-refresh').show();
      }
    }
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
    return StatsAPI.getStats(this.pootlePath)
      .done((data) => this.setState({ data }))
      .always(() => $('body').spin(false));
  },

  handleToggleAllItems({ showAll }) {
    if (this.fullItem) {
      this.setState({
        item: showAll ? this.fullItem : this.initialItem,
      });
      return;
    }

    const includeDisabled = true;
    $('body').spin();
    StatsAPI.getStats(this.pootlePath, includeDisabled)
      .done((data) => {
        this.fullItem = getItem(data, this.pootlePath);
        this.setState({
          item: this.fullItem,
          items: data.children,
        });
      })
      .always(() => {
        $('body').spin(false);
      });
  },

  updateUI() {
    this.updateStatsUI();

    const areTranslateActionsEnabled = this.hasAdminAccess || this.languageCode;
    ReactDOM.render(
      <ActionBar
        canAdminDueDates={this.canAdminDueDates}
        initialDueDate={this.initialDueDate}
        areTranslateActionsEnabled={areTranslateActionsEnabled}
        pootlePath={this.pootlePath}
        stats={this.state.item}
      />,
      q('.js-mnt-action-bar')
    );

    ReactDOM.render(
      <StatsSummary
        isInitiallyExpanded={this.isInitiallyExpanded}
        canTranslate={this.canTranslateStats}
        hasMoreContributors={this.state.topContributorsData.has_more_items}
        pootlePath={this.pootlePath}
        stats={this.state.item}
        topContributorsData={this.state.topContributorsData.items}
      />,
      q('.js-mnt-stats-summary')
    );

    ReactDOM.render(
      <BrowserTable
        hasDisabledItems={this.hasDisabledItems}
        items={this.state.items}
        isInitiallyDisabled={this.initialItem.is_disabled}
        onToggleAllItems={(opts) => this.handleToggleAllItems(opts)}
      />,
      q('#js-browsing-table-container')
    );
  },
};

export default stats;
