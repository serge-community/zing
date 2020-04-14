/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';

import CaretIcon from './CaretIcon';


const CLICK_FREQUENCY = 100;


const CaretButton = React.createClass({

  propTypes: {
    disabled: React.PropTypes.bool,
    direction: React.PropTypes.oneOf(['up', 'down']).isRequired,
    onClick: React.PropTypes.func,
    style: React.PropTypes.object,
    title: React.PropTypes.string,
  },

  componentWillMount() {
    this.isMouseDown = false;
  },

  handleMouseDown(e) {
    if (!this.props.onClick || this.props.disabled) {
      e.stopPropagation();
      return;
    }

    this.isMouseDown = true;

    this.clickTimer = setInterval(() => {
      this.props.onClick(e);
    }, CLICK_FREQUENCY);
  },

  handleMouseOut(e) {
    clearInterval(this.clickTimer);

    if (this.isMouseDown) {
      this.props.onClick(e);
    }

    this.isMouseDown = false;
  },

  render() {
    const { direction, disabled } = this.props;

    const wrapperStyle = Object.assign({}, {
      padding: '0.2em',
      msUserSelect: 'none',
      MozUserSelect: 'none',
      WebkitUserSelect: 'none',
      userSelect: 'none',
    }, this.props.style);

    const iconStyle = {
      fill: '#666',
    };
    if (disabled) {
      iconStyle.fill = '#9F9F9F';
    }

    return (
      <div
        onMouseDown={this.handleMouseDown}
        onMouseOut={this.handleMouseOut}
        onMouseUp={this.handleMouseOut}
        title={this.props.title}
        style={wrapperStyle}
      >
        <CaretIcon style={iconStyle} direction={direction} />
      </div>
    );
  },

});


export default CaretButton;
