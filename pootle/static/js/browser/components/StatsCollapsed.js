/*
 * Copyright (C) Pootle contributors.
 *
 * This file is a part of the Pootle project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React, { PropTypes } from 'react';

import Avatar from 'components/Avatar';
import { t } from 'utils/i18n';

const StatsCollapsed = React.createClass({
    propTypes: {
        topContributors: React.PropTypes.array.isRequired,
    },

    getScoreTextfunction: function(score) {
        if (score > 0) {
            return t('+%(score)s', { score });
        }
        return score;
    },

    createRow: function(item, index) {
        const position = index + 1;
        return (
            <li key={item.username} className="top-scorer">
                <div className="place">{t('#%(position)s', { position })}</div>
                <div className="user">
                    <Avatar
                        email={item.email}
                        label={item.display_name}
                        size={20}
                        username={item.username}
                    />
                </div>
                <div className="number">{this.getScoreTextfunction(item.public_total_score)}</div>
            </li>
        );
    },

    render: function() {
        if (this.props.topContributors.length == 0) {
            return(
                <label className="placeholder">
                    {t('There was no activity here for the past 30 days')}
                </label>
            );
        }
        return (
            <div>
                <label>{t('Top contributors:')}</label>
                <ul className="top-scorers">
                    {this.props.topContributors.slice(0, 3).map(this.createRow)}
                </ul>
                <div className="clear"></div>
            </div>
        );
    },
});

export default StatsCollapsed;
