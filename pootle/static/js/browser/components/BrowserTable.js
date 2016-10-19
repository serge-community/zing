/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';

import TextToggle from 'components/TextToggle';
import { t } from 'utils/i18n';

import BrowserTableRow from './BrowserTableRow';


const COL_TITLE = 0;
const COL_PROGRESS = 1;
const COL_TOTAL = 2;
const COL_LASTUPDATED = 3;
const COL_CRITICAL = 4;
const COL_SUGGESTIONS = 5;
const COL_INCOMPLETE = 6;
const COL_LASTACTIVITY = 7;


function sortFunc(a, b, items, sortColumn) {
  const ia = items[a];
  const ib = items[b];
  const col = sortColumn;

  if (col === COL_TITLE) {
    const typeA = ia.treeitem_type || 0;
    const typeB = ib.treeitem_type || 0;
    if (typeA !== typeB) {
      return typeB - typeA;
    }
    return ia.title.localeCompare(ib.title);
  }

  if (col === COL_PROGRESS) {
    return ia.progress - ib.progress;
  }

  if (col === COL_TOTAL) {
    return ia.total - ib.total;
  }

  if (col === COL_LASTUPDATED) {
    return ib.lastupdated - ia.lastupdated; // reversed
  }

  if (col === COL_CRITICAL) {
    return ia.critical - ib.critical;
  }

  if (col === COL_SUGGESTIONS) {
    return ia.suggestions - ib.suggestions;
  }

  if (col === COL_INCOMPLETE) {
    return ia.incomplete - ib.incomplete;
  }

  if (col === COL_LASTACTIVITY) {
    return ib.lastaction.mtime - ia.lastaction.mtime; // reversed
  }

  throw new Error(`Sort column index out of range: ${sortColumn}`);
}


const BrowserTable = React.createClass({

  propTypes: {
    items: React.PropTypes.array.isRequired,
  },

  getDefaultProps() {
    return {
      items: [],
    };
  },

  getInitialState() {
    return {
      showDisabledRows: false,
      sortColumn: COL_TITLE,
      reverseSort: false,
    };
  },

  componentWillMount() {
    this.hasDisabledItems = this.hasAnyDisabledItems(this.props.items);
    this.sortedKeys = Object.keys(this.props.items).sort((a, b) => (
      sortFunc(a, b, this.props.items, this.state.sortColumn)
    ));
  },

  componentWillUpdate(nextProps, nextState) {
    this.hasDisabledItems = this.hasAnyDisabledItems(nextProps.items);

    if (this.state.sortColumn !== nextState.sortColumn) {
      this.sortedKeys = this.sortedKeys.sort((a, b) => (
        sortFunc(a, b, nextProps.items, nextState.sortColumn)
      ));
      return;
    }

    if (this.state.reverseSort !== nextState.reverseSort) {
      // quick reverse
      this.sortedKeys = this.sortedKeys.reverse();
    }
  },

  getClassName(colN) {
    if (colN === this.state.sortColumn) {
      return this.state.reverseSort ? 'reverse' : 'normal';
    }
    return '';
  },

  handleHeaderClick(colN) {
    let { reverseSort, sortColumn } = this.state;
    if (sortColumn === colN) {
      reverseSort = !reverseSort;
    } else {
      sortColumn = colN;
      reverseSort = false;
    }
    this.setState({ reverseSort, sortColumn });
  },

  // check if there are disabled items
  hasAnyDisabledItems(items) {
    for (const key in items) {
      if (items[key].is_disabled) {
        return true;
      }
    }
    return false;
  },

  handleDisabledRowsVisibility({ isActive }) {
    this.setState({ showDisabledRows: isActive });
  },

  createRow(key) {
    const item = this.props.items[key];
    if (!this.state.showDisabledRows &&
        (item.hasOwnProperty('is_disabled') && item.is_disabled)) {
      return null;
    }

    return (
      <BrowserTableRow
        critical={item.critical}
        fuzzy={item.fuzzy}
        key={key}
        lastAction={item.lastaction}
        lastUpdated={item.lastupdated}
        isDisabled={item.is_disabled}
        isDirty={item.is_dirty}
        itemType={item.treeitem_type}
        pootlePath={item.pootle_path}
        suggestions={item.suggestions}
        title={item.title}
        total={item.total}
        translated={item.translated}
      />
    );
  },

  render() {
    if (!this.sortedKeys.length) {
      return null;
    }

    let toggle = null;
    if (this.hasDisabledItems) {
      toggle = (
        <TextToggle
          defaultChecked
          labelActive={t('Show disabled')}
          labelInactive={t('Hide disabled')}
          onClick={this.handleDisabledRowsVisibility}
          className="toggle admin"
        />
      );
    }

    return (
      <table className="browser-table-component stats">
        <thead>
        <tr>
          <th className="stats">
            <label
              className={this.getClassName(COL_TITLE)}
              onClick={() => this.handleHeaderClick(COL_TITLE)}
            >
              {t('Name')}
            </label>
            &nbsp;
            {toggle}
          </th>

          <th className="stats">
            <label
              className={this.getClassName(COL_PROGRESS)}
              onClick={() => this.handleHeaderClick(COL_PROGRESS)}
            >
              {t('Progress')}
            </label>
          </th>

          <th className="stats-number">
            <label
              className={this.getClassName(COL_TOTAL)}
              onClick={() => this.handleHeaderClick(COL_TOTAL)}
            >
              {t('Total')}
            </label>
          </th>

          <th className="stats-number">
            <label
              className={this.getClassName(COL_LASTUPDATED)}
              onClick={() => this.handleHeaderClick(COL_LASTUPDATED)}
            >
              {t('Last updated')}
            </label>
          </th>

          <th className="stats-number">
            <label
              className={this.getClassName(COL_CRITICAL)}
              onClick={() => this.handleHeaderClick(COL_CRITICAL)}
            >
              {t('Critical')}
            </label>
          </th>

          <th className="stats-number">
            <label
              className={this.getClassName(COL_SUGGESTIONS)}
              onClick={() => this.handleHeaderClick(COL_SUGGESTIONS)}
            >
              {t('Suggestions')}
            </label>
          </th>

          <th className="stats-number">
            <label
              className={this.getClassName(COL_INCOMPLETE)}
              onClick={() => this.handleHeaderClick(COL_INCOMPLETE)}
            >
              {t('Incomplete')}
            </label>
          </th>

          <th className="stats">
            <label
              className={this.getClassName(COL_LASTACTIVITY)}
              onClick={() => this.handleHeaderClick(COL_LASTACTIVITY)}
            >
              {t('Last Activity')}
            </label>
          </th>
        </tr>
        </thead>
        <tbody className="stats">
          {this.sortedKeys.map(this.createRow)}
        </tbody>
      </table>
    );
  },
});

export default BrowserTable;
