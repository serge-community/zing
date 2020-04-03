/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import cx from 'classnames';
import React from 'react';

import { getTranslateUrl } from 'utils/url';

const CheckItem = ({ canTranslate, item, url }) => {
  if (canTranslate) {
    return (
      <a className="check-data" href={url}>
        {item}
      </a>
    );
  }

  return <span className="check-data">{item}</span>;
};
CheckItem.propTypes = {
  canTranslate: React.PropTypes.bool.isRequired,
  item: React.PropTypes.oneOfType([React.PropTypes.string, React.PropTypes.number])
    .isRequired,
  url: React.PropTypes.string.isRequired,
};

const CheckRow = ({ check, canTranslate, pootlePath }) => {
  const classNames = cx(
    {
      'category-critical': check.is_critical,
    },
    'check'
  );

  let url = '';
  if (canTranslate) {
    url = getTranslateUrl(pootlePath, { checks: check.code });
  }

  const props = { canTranslate, url };

  return (
    <tr className={classNames}>
      <td className="check-name">
        <CheckItem item={check.title} {...props} />
      </td>
      <td className="check-count">
        <CheckItem item={check.count} {...props} />
      </td>
    </tr>
  );
};
CheckRow.propTypes = {
  check: React.PropTypes.object.isRequired,
  canTranslate: React.PropTypes.bool.isRequired,
  pootlePath: React.PropTypes.string.isRequired,
};

const FailingChecksTable = ({ items, canTranslate, pootlePath }) => {
  const props = { canTranslate, pootlePath };
  return (
    <table>
      <tbody>
        {items.map((item) => (
          <CheckRow key={item.code} check={item} {...props} />
        ))}
      </tbody>
    </table>
  );
};
FailingChecksTable.propTypes = {
  items: React.PropTypes.array.isRequired,
  canTranslate: React.PropTypes.bool.isRequired,
  pootlePath: React.PropTypes.string.isRequired,
};

export default FailingChecksTable;
