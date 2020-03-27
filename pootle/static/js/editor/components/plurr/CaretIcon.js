/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';

const CaretIcon = React.createClass({
  propTypes: {
    direction: React.PropTypes.oneOf(['up', 'down']).isRequired,
    style: React.PropTypes.object,
  },

  renderUp() {
    return (
      <g
        id="Core"
        transform="translate(-553.000000, -9.000000)"
        {...this.props.style}
      >
        <g id="arrow-drop-up" transform="translate(553.000000, 9.500000)">
          <path d="M0,5 L5,0 L10,5 L0,5 Z" id="Shape" />
        </g>
      </g>
    );
  },

  renderDown() {
    return (
      <g
        id="Core"
        transform="translate(-469.000000, -9.000000)"
        {...this.props.style}
      >
        <g id="arrow-drop-down" transform="translate(469.000000, 9.500000)">
          <path d="M0,0 L5,5 L10,0 L0,0 Z" id="Shape" />
        </g>
      </g>
    );
  },

  render() {
    return (
      <svg
        version="1.1"
        viewBox="0 0 10 7"
        height="6px"
        width="8px"
        xmlns="http://www.w3.org/2000/svg"
        style={{ display: 'block' }}
      >
        <g
          fill="none"
          fill-rule="evenodd"
          id="CaretIcon"
          stroke="none"
          strokeWidth="1"
        >
          {this.props.direction === 'up' ? this.renderUp() : this.renderDown()}
        </g>
      </svg>
    );
  },
});

export default CaretIcon;
