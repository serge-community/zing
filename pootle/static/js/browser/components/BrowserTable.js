/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import cx from 'classnames';
import React, { PropTypes } from 'react';

import TextToggle from 'components/TextToggle';
import TimeSince from 'components/TimeSince';
import LastActivity from 'components/LastActivity';
import { t } from 'utils/i18n';

const ColoredNumber = React.createClass({
    propTypes: {
        n: React.PropTypes.number,
    },

    render: function() {
        if (!this.props.n) {
            return (<span className="zero">0</span>);
        }
        return (
            <span>{this.props.n}</span>
        );
    }
});

const NumberPill = React.createClass({
    propTypes: {
        n: React.PropTypes.number,
        url: React.PropTypes.string.isRequired,
    },

    render: function() {
        if (!this.props.n) {
            return (<span className="zero">0</span>);
        }
        return (
            <a className="stats-data" href={this.props.url}>{this.props.n}</a>
        );
    }
});

const ProgressBar = React.createClass({
    render: function() {
        var total = this.props.total || 0;
        var fuzzy = this.props.fuzzy || 0;
        var trans = this.props.translated || 0;
        var trans_p = total > 0 ? Math.round(trans / total * 100) : 100;
        var fuzzy_p = total > 0 ? Math.round(fuzzy / total * 100) : 0;
        var untrans_p = 100 - trans_p - fuzzy_p;

        var title= '<span class="legend translated"></span><span class="value translated">'+trans_p+'</span>% translated<br/>'+
            '<span class="legend fuzzy"></span><span class="value fuzzy">'+fuzzy_p+'</span>% needs work<br/>'+
            '<span class="legend untranslated"></span><span class="value untranslated">'+untrans_p+'</span>% untranslated';

        return (
            <table className="graph" title={title}>
                <tbody>
                    <tr>
                        <td className="translated" style={{'width': trans_p+'%'}}><span></span></td>
                        <td className="fuzzy" style={{'width': fuzzy_p+'%'}}><span></span></td>
                        <td className="untranslated"><span></span></td>
                    </tr>
                </tbody>
            </table>
        );
    }
});

const BrowserTable = React.createClass({

    propTypes: {
        items: React.PropTypes.array.isRequired,
    },

    // TODO: is there a better way to define constants (not fields)?
    COL_TITLE: 0,
    COL_PROGRESS: 1,
    COL_TOTAL: 2,
    COL_LASTUPDATED: 3,
    COL_CRITICAL: 4,
    COL_SUGGESTIONS: 5,
    COL_INCOMPLETE: 6,
    COL_LASTACTIVITY: 7,

    getInitialState : function() {
        return {
            showDisabledRows: false,
            sortColumn: this.COL_TITLE,
            reverseSort: false,
        };
    },

    componentWillMount() {
        // check if there are disabled items
        this.hasDisabledItems = false;
        for (var key in this.props.items) {
            var item = this.props.items[key];
            if (item.is_disabled) {
                this.hasDisabledItems = true;
                break;
            }
        }

        this.sortedKeys = Object.keys(this.props.items).sort(this.sortFunc);
    },

    handleDisabledRowsVisibility({ isActive: state }) {
        var s = this.state;
        s.showDisabledRows = state;
        this.setState(s);
    },

    sortFunc(a, b) {
        var ia = this.props.items[a];
        var ib = this.props.items[b];

        if (this.state.sortColumn == this.COL_TITLE) {
            return ia.title.localeCompare(ib.title);
        }

        if (this.state.sortColumn == this.COL_PROGRESS) {
            return ia.progress - ib.progress;
        }

        if (this.state.sortColumn == this.COL_TOTAL) {
            return ia.total - ib.total;
        }

        if (this.state.sortColumn == this.COL_LASTUPDATED) {
            return ib.lastupdated - ia.lastupdated; // reversed
        }

        if (this.state.sortColumn == this.COL_CRITICAL) {
            return ia.critical - ib.critical;
        }

        if (this.state.sortColumn == this.COL_SUGGESTIONS) {
            return ia.suggestions - ib.suggestions;
        }

        if (this.state.sortColumn == this.COL_INCOMPLETE) {
            return ia.incomplete - ib.incomplete;
        }

        if (this.state.sortColumn == this.COL_LASTACTIVITY) {
            return ib.lastaction.mtime - ia.lastaction.mtime; // reversed
        }

        throw new Error('Sort column index out of range: '+this.state.sortColumn);
    },

    handleHeaderClick(colN) {
        var s = this.state;
        if (s.sortColumn == colN) {
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

    getClassName(colN) {
        if (colN == this.state.sortColumn) {
            return this.state.reverseSort ? 'reverse' : 'normal'
        }
    },

    createRow(key, index) {
        var i = this.props.items[key];

        if (i.is_disabled && !this.state.showDisabledRows) {
            return;
        }

        const trClasses = cx('item', {
            'is-visible': true, // TODO: remove?
            'is-disabled': i.is_disabled,
            'is-dirty': i.is_dirty,
        });

        var icon = 'icon-file';
        if (i.treeitem_type == 1) icon = 'icon-folder';
        if (i.treeitem_type == 2) icon = 'icon-project';

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
                        url={i.translate_url + '#filter=checks&category=critical'}
                    />
                </td>
                <td className="stats-number suggestions">
                    <NumberPill
                        n={i.suggestions}
                        url={i.translate_url + '#filter=suggestions'}
                    />
                </td>
                <td className="stats-number need-translation">
                    <NumberPill
                        n={i.total - i.translated}
                        url={i.translate_url + '#filter=incomplete'}
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
                <noscript/>
            );
        }

        var toggle = '';
        if (this.hasDisabledItems) {
            toggle = <TextToggle
                defaultChecked
                labelActive={t('Show disabled')}
                labelInactive={t('Hide disabled')}
                onClick={this.handleDisabledRowsVisibility}
                className="toggle admin"
            />
        }

        return (
            <table className="browser-table-component stats">
                <thead>
                    <tr>
                        <th className="stats">
                            <label className={this.getClassName(this.COL_TITLE)}
                                   onClick={() => {this.handleHeaderClick(this.COL_TITLE)}}>
                                {t('Name')}
                            </label>
                            &nbsp;
                            {toggle}
                        </th>

                        <th className="stats">
                            <label className={this.getClassName(this.COL_PROGRESS)}
                                   onClick={() => {this.handleHeaderClick(this.COL_PROGRESS)}}>
                                {t('Progress')}
                            </label>
                        </th>

                        <th className="stats-number">
                            <label className={this.getClassName(this.COL_TOTAL)}
                                   onClick={() => {this.handleHeaderClick(this.COL_TOTAL)}}>
                                {t('Total')}
                            </label>
                        </th>

                        <th className="stats-number">
                            <label className={this.getClassName(this.COL_LASTUPDATED)}
                                   onClick={() => {this.handleHeaderClick(this.COL_LASTUPDATED)}}>
                                {t('Last updated')}
                            </label>
                        </th>

                        <th className="stats-number">
                            <label className={this.getClassName(this.COL_CRITICAL)}
                                   onClick={() => {this.handleHeaderClick(this.COL_CRITICAL)}}>
                                {t('Critical')}
                            </label>
                        </th>

                        <th className="stats-number">
                            <label className={this.getClassName(this.COL_SUGGESTIONS)}
                                   onClick={() => {this.handleHeaderClick(this.COL_SUGGESTIONS)}}>
                                {t('Suggestions')}
                            </label>
                        </th>

                        <th className="stats-number">
                            <label className={this.getClassName(this.COL_INCOMPLETE)}
                                   onClick={() => {this.handleHeaderClick(this.COL_INCOMPLETE)}}>
                                {t('Incomplete')}
                            </label>
                        </th>

                        <th className="stats">
                            <label className={this.getClassName(this.COL_LASTACTIVITY)}
                                   onClick={() => {this.handleHeaderClick(this.COL_LASTACTIVITY)}}>
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
