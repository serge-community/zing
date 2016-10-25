/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import _ from 'underscore';

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

class AutoIcon extends React.Component {

  static propTypes() {
    return {
      title: React.PropTypes.string.isRequired,
      saturation: React.PropTypes.number,
      lightness: React.PropTypes.number,
      abbreviationLength: React.PropTypes.number,
      mode: React.PropTypes.string,
      size: React.PropTypes.number,
    };
  }

  constructor(props) {
    super();

    this.state = _.extend({
      saturation: 100,
      lightness: 30,
      abbreviationLength: 2,
      mode: 'solid',
      size: 20,
    }, props);
  }

  componentDidMount() {
    this.calculateProps(this.props.title);
  }

  componentWillReceiveProps(newProps) {
    if (this.props.title !== newProps.title) {
      this.calculateProps(newProps.title);
    }
  }

  calculateProps(title) {
    this.setState({
      abbreviation: calcAbbreviation(title, this.state.abbreviationLength),
      hue: calcHue(title),
    });
  }

  render() {
    const color =
      `hsl(${this.state.hue}, ${this.state.saturation}%, ${this.state.lightness}%)`;

    const size = `${this.state.size}px`;
    const fontSize = `${Math.round(this.state.size / 2)}px`;

    const style = (this.state.mode === 'solid') ? {
      backgroundColor: color,
      border: `1px solid ${color}`,
      color: '#fff',
      width: size,
      height: size,
      lineHeight: size,
      fontSize,
    } : {
      border: `1px solid ${color}`,
      color,
      width: size,
      height: size,
      lineHeight: size,
      fontSize,
    };

    return (
      <span
        className="auto-icon"
        style={style}
      >{this.state.abbreviation}</span>
    );
  }

}


export default AutoIcon;
