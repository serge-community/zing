/*
 * Copyright (C) Pootle contributors.
 *
 * This file is a part of the Pootle project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';

import Avatar from 'components/Avatar';
import { t, nt } from 'utils/i18n';
import { getScoreText } from 'utils/score';

function createRow(item, index) {
  const titleParts = [];
  if (item.suggested > 0) {
    titleParts.push(
      nt('%(units)s suggested', '%(units)s suggested', item.suggested, {
        units: `<span class="value">${item.suggested}</span>`,
      })
    );
  }

  if (item.translated > 0) {
    titleParts.push(
      nt('%(units)s translated', '%(units)s translated', item.translated, {
        units: `<span class="value">${item.translated}</span>`,
      })
    );
  }

  if (item.reviewed > 0) {
    titleParts.push(
      nt('%(units)s reviewed', '%(units)s reviewed', item.reviewed, {
        units: `<span class="value">${item.reviewed}</span>`,
      })
    );
  }

  return (
    <tr key={`top-contibutor-${index}`}>
      <td className="number">{t('#%(position)s', { position: index + 1 })}</td>
      <td className="user top-scorer">
        <Avatar
          email={item.email}
          displayName={item.display_name}
          size={20}
          username={item.username}
        />
      </td>
      <td className="number">
        <span title={titleParts.join('<br />')}>
          {getScoreText(item.public_total_score)}
        </span>
      </td>
    </tr>
  );
}

const TopContributorsTable = ({ items }) => (
  <table className="top-scorers-table">
    <tbody>{items.map(createRow)}</tbody>
  </table>
);

TopContributorsTable.propTypes = {
  items: React.PropTypes.array.isRequired,
};

export default TopContributorsTable;
