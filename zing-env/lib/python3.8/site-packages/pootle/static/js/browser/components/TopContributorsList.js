/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';

import Avatar from 'components/Avatar';
import { t } from 'utils/i18n';
import { getScoreText } from 'utils/score';


const TopContributorsList = React.createClass({
  propTypes: {
    topContributors: React.PropTypes.array.isRequired,
  },

  getDefaultProps() {
    return {
      topContributors: [],
    };
  },

  createRow(item, index) {
    const position = index + 1;
    return (
      <li key={item.username} className="top-scorer">
        <div className="place">{t('#%(position)s', { position })}</div>
        <div className="user">
          <Avatar
            email={item.email}
            displayName={item.display_name}
            size={20}
            username={item.username}
          />
        </div>
        <div className="number">{getScoreText(item.public_total_score)}</div>
      </li>
    );
  },

  render() {
    if (this.props.topContributors.length === 0) {
      return (
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

export default TopContributorsList;
