/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import cx from 'classnames';
import React from 'react';

import LastActivity from 'components/LastActivity';
import TimeSince from 'components/TimeSince';
import { getTranslateUrl } from 'utils/url';

import ColoredNumber from './ColoredNumber';
import NumberPill from './NumberPill';
import ProgressBar from './ProgressBar';


const ITEM_FILE = 0;
const ITEM_FOLDER = 1;
const ITEM_PROJECT = 2;
const ITEM_LANGUAGE = 3;


const BrowserTableRow = React.createClass({

  propTypes: {
    critical: React.PropTypes.number,
    fuzzy: React.PropTypes.number,
    isDisabled: React.PropTypes.bool,
    isDirty: React.PropTypes.bool,
    itemType: React.PropTypes.number,
    lastAction: React.PropTypes.object,
    lastUpdated: React.PropTypes.number,
    pootlePath: React.PropTypes.string.isRequired,
    suggestions: React.PropTypes.number,
    title: React.PropTypes.string.isRequired,
    total: React.PropTypes.number,
    translated: React.PropTypes.number,
  },

  getDefaultProps() {
    return {
      critical: 0,
      fuzzy: 0,
      lastAction: {},
      lastUpdated: 0,
      isDisabled: false,
      isDirty: false,
      itemType: ITEM_FILE,
      suggestions: 0,
      translated: 0,
      total: 0,
    };
  },

  render() {
    const {
      critical, fuzzy, isDisabled, isDirty, itemType, lastAction, lastUpdated,
      pootlePath, suggestions, title, total, translated,
    } = this.props;

    const trClasses = cx('item', {
      'is-disabled': isDisabled,
      'is-empty': total === 0,
      'is-dirty': isDirty,
    });

    let itemTypeName;
    if (itemType === ITEM_FILE) itemTypeName = 'file';
    if (itemType === ITEM_FOLDER) itemTypeName = 'folder';
    if (itemType === ITEM_PROJECT) itemTypeName = 'project';
    if (itemType === ITEM_LANGUAGE) itemTypeName = 'language';

    const progressBar = total === 0 ? null :
      <ProgressBar
        total={total}
        fuzzy={fuzzy}
        translated={translated}
      />;

    return (
      <tr className={trClasses}>
        <td className={cx('stats-name', itemTypeName)}>
          <a href={pootlePath} title={title}>
            <i className={`icon-${itemTypeName}`} />{title}
          </a>
        </td>
        <td className="stats-graph">
          {progressBar}
        </td>
        <td className="stats-number total">
          <a href={getTranslateUrl(pootlePath)} className="stats-data">
            <ColoredNumber n={total} />
          </a>
        </td>
        <td className="stats-number last-updated">
          <TimeSince timestamp={lastUpdated} />
        </td>
        <td className="stats-number critical">
          <NumberPill
            n={critical}
            url={`${getTranslateUrl(pootlePath)}#filter=checks&category=critical`}
          />
        </td>
        <td className="stats-number suggestions">
          <NumberPill
            n={suggestions}
            url={`${getTranslateUrl(pootlePath)}#filter=suggestions`}
          />
        </td>
        <td className="stats-number need-translation">
          <NumberPill
            n={total - translated}
            url={`${getTranslateUrl(pootlePath)}#filter=incomplete`}
          />
        </td>
        <td className="last-activity">
          <LastActivity {...lastAction} />
        </td>
      </tr>
    );
  },
});

export default BrowserTableRow;
