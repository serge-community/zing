/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import cx from 'classnames';
import React from 'react';

import ColoredNumber from './ColoredNumber';
import NumberPill from './NumberPill';
import ProgressBar from './ProgressBar';
import TextToggle from 'components/TextToggle';
import TimeSince from 'components/TimeSince';
import LastActivity from 'components/LastActivity';
import { t } from 'utils/i18n';

const COL_TITLE = 0;
const COL_PROGRESS = 1;
const COL_TOTAL = 2;
const COL_LASTUPDATED = 3;
const COL_CRITICAL = 4;
const COL_SUGGESTIONS = 5;
const COL_INCOMPLETE = 6;
const COL_LASTACTIVITY = 7;

const BrowserTable = React.createClass({

  propTypes: {
    items: React.PropTypes.array.isRequired,
  },

  getInitialState() {
    return {
      showDisabledRows: false,
      sortColumn: COL_TITLE,
      reverseSort: false,
    };
  },

  componentWillMount() {
    // check if there are disabled items
    this.hasDisabledItems = false;
    for (const key in this.props.items) {
      if (this.props.items[key].is_disabled) {
        this.hasDisabledItems = true;
        break;
      }
    }

    this.sortedKeys = Object.keys(this.props.items).sort(this.sortFunc);
  },

  getClassName(colN) {
    if (colN === this.state.sortColumn) {
      return this.state.reverseSort ? 'reverse' : 'normal';
    }
    return '';
  },

  handleHeaderClick(colN) {
    const s = this.state;
    if (s.sortColumn === colN) {
      // quick reverse
      s.reverseSort = !s.reverseSort;
      this.sortedKeys = this.sortedKeys.reverse();
    } else {
      s.sortColumn = colN;
      s.reverseSort = false;
      this.sortedKeys = this.sortedKeys.sort(this.sortFunc);
    }
    this.setState(s);
  },

  sortFunc(a, b) {
    const ia = this.props.items[a];
    const ib = this.props.items[b];

    if (this.state.sortColumn === COL_TITLE) {
      return ia.title.localeCompare(ib.title);
    }

    if (this.state.sortColumn === COL_PROGRESS) {
      return ia.progress - ib.progress;
    }

    if (this.state.sortColumn === COL_TOTAL) {
      return ia.total - ib.total;
    }

    if (this.state.sortColumn === COL_LASTUPDATED) {
      return ib.lastupdated - ia.lastupdated; // reversed
    }

    if (this.state.sortColumn === COL_CRITICAL) {
      return ia.critical - ib.critical;
    }

    if (this.state.sortColumn === COL_SUGGESTIONS) {
      return ia.suggestions - ib.suggestions;
    }

    if (this.state.sortColumn === COL_INCOMPLETE) {
      return ia.incomplete - ib.incomplete;
    }

    if (this.state.sortColumn === COL_LASTACTIVITY) {
      return ib.lastaction.mtime - ia.lastaction.mtime; // reversed
    }

    throw new Error(`Sort column index out of range: ${this.state.sortColumn}`);
  },

  handleDisabledRowsVisibility({ isActive: state }) {
    const s = this.state;
    s.showDisabledRows = state;
    this.setState(s);
  },

  createRow(key) {
    const i = this.props.items[key];

    if (i.is_disabled && !this.state.showDisabledRows) {
      return null;
    }

    const trClasses = cx('item', {
      'is-visible': true, // TODO: remove?
      'is-disabled': i.is_disabled,
      'is-dirty': i.is_dirty,
    });

    let icon = 'icon-file';
    if (i.treeitem_type === 1) icon = 'icon-folder';
    if (i.treeitem_type === 2) icon = 'icon-project';

    return (
      <tr key={key} className={trClasses}>
        <td className="stats-name">
          <a href={i.pootle_path} title={i.title}><i className={icon} />{i.title}</a>
        </td>
        <td className="stats-graph"><ProgressBar
          total={i.total}
          fuzzy={i.fuzzy}
          translated={i.translated}
        /></td>
        <td className="stats-number total">
          <a href={i.translate_url} className="stats-data">
            <ColoredNumber n={i.total} />
          </a>
        </td>
        <td className="stats-number last-updated">
          <TimeSince timestamp={i.lastupdated} />
        </td>
        <td className="stats-number critical">
          <NumberPill
            n={i.critical}
            url={`${i.translate_url}#filter=checks&category=critical`}
          />
        </td>
        <td className="stats-number suggestions">
          <NumberPill
            n={i.suggestions}
            url={`${i.translate_url}#filter=suggestions`}
          />
        </td>
        <td className="stats-number need-translation">
          <NumberPill
            n={i.total - i.translated}
            url={`${i.translate_url}#filter=incomplete`}
          />
        </td>
        <td className="last-activity">
          <LastActivity {...i.lastaction} />
        </td>
      </tr>
    );
  },

  render() {
    if (!this.sortedKeys.length) {
      // TODO: provide styling for the message
      return (
        <noscript />
      );
    }

    let toggle = '';
    if (this.hasDisabledItems) {
      toggle = (<TextToggle
        defaultChecked
        labelActive={t('Show disabled')}
        labelInactive={t('Hide disabled')}
        onClick={this.handleDisabledRowsVisibility}
        className="toggle admin"
      />);
    }

    return (
      <table className="browser-table-component stats">
        <thead>
        <tr>
          <th className="stats">
            <label className={this.getClassName(COL_TITLE)}
              onClick={() => {this.handleHeaderClick(COL_TITLE);}}
            >
              {t('Name')}
            </label>
            &nbsp;
            {toggle}
          </th>

          <th className="stats">
            <label className={this.getClassName(COL_PROGRESS)}
              onClick={() => {this.handleHeaderClick(COL_PROGRESS);}}
            >
              {t('Progress')}
            </label>
          </th>

          <th className="stats-number">
            <label className={this.getClassName(COL_TOTAL)}
              onClick={() => {this.handleHeaderClick(COL_TOTAL);}}
            >
              {t('Total')}
            </label>
          </th>

          <th className="stats-number">
            <label className={this.getClassName(COL_LASTUPDATED)}
              onClick={() => {this.handleHeaderClick(COL_LASTUPDATED);}}
            >
              {t('Last updated')}
            </label>
          </th>

          <th className="stats-number">
            <label className={this.getClassName(COL_CRITICAL)}
              onClick={() => {this.handleHeaderClick(COL_CRITICAL);}}
            >
              {t('Critical')}
            </label>
          </th>

          <th className="stats-number">
            <label className={this.getClassName(COL_SUGGESTIONS)}
              onClick={() => {this.handleHeaderClick(COL_SUGGESTIONS);}}
            >
              {t('Suggestions')}
            </label>
          </th>

          <th className="stats-number">
            <label className={this.getClassName(COL_INCOMPLETE)}
              onClick={() => {this.handleHeaderClick(COL_INCOMPLETE);}}
            >
              {t('Incomplete')}
            </label>
          </th>

          <th className="stats">
            <label className={this.getClassName(COL_LASTACTIVITY)}
              onClick={() => {this.handleHeaderClick(COL_LASTACTIVITY);}}
            >
              {t('Last Activity')}
            </label>
          </th>
        </tr>
        </thead>
        <tbody className="stats js-browsing-table">
        {this.sortedKeys.map(this.createRow)}
        </tbody>
      </table>
    );
  },
});

export default BrowserTable;
