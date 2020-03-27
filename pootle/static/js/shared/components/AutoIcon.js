/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';

import crc16 from '../utils/crc16'; // use relative path, otherwise tests will fail

function calcAbbreviation(title, length) {
  const regexA = /\b[A-Z]/g;
  const regexB = /\b[\w]/g;

  let out = [];
  let matches;
  while ((matches = regexA.exec(title))) {
    out.push(matches[0]);
    if (out.length === length) {
      return out.join('');
    }
  }

  out = [];
  while ((matches = regexB.exec(title))) {
    out.push(matches[0]);
    if (out.length === length) {
      return out.join('').toUpperCase();
    }
  }

  return title.substr(0, length).toUpperCase();
}

function calcHue(title) {
  return crc16(title) % 360;
}

const AutoIcon = ({
  title,
  saturation = 100,
  lightness = 30,
  abbreviationLength = 2,
  mode = 'solid',
  size = 20,
}) => {
  const abbreviation = calcAbbreviation(title, abbreviationLength);
  const hue = calcHue(title);

  const color = `hsl(${hue}, ${saturation}%, ${lightness}%)`;

  const sizePx = `${size}px`;
  const fontSizePx = `${Math.round(size / 2)}px`;

  const style = {
    backgroundColor: '#fff',
    border: `1px solid ${color}`,
    color,
    width: sizePx,
    height: sizePx,
    lineHeight: sizePx,
    fontSize: fontSizePx,
  };

  if (mode === 'solid') {
    style.backgroundColor = color;
    style.color = '#fff';
  }

  return (
    <span className="auto-icon" style={style}>
      {abbreviation}
    </span>
  );
};

AutoIcon.propTypes = {
  title: React.PropTypes.string.isRequired,
  saturation: React.PropTypes.number,
  lightness: React.PropTypes.number,
  abbreviationLength: React.PropTypes.number,
  mode: React.PropTypes.string,
  size: React.PropTypes.number,
};

export default AutoIcon;
