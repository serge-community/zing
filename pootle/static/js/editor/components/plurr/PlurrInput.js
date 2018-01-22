/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';

import CaretButton from './CaretButton';


const isInteger = (val) => /^\d+$/.test(val);


const PlurrInput = React.createClass({

  propTypes: {
    min: React.PropTypes.number,
    name: React.PropTypes.string.isRequired,
    onChange: React.PropTypes.func.isRequired,
    step: React.PropTypes.number,
    style: React.PropTypes.object,
    tabIndex: React.PropTypes.number,
    value: React.PropTypes.string.isRequired,
  },

  getDefaultProps() {
    return {
      min: 0,
      step: 1,
    };
  },

  getInitialState() {
    return {
      focus: false,
      hover: false,
    };
  },

  componentDidUpdate(prevProps) {
    const prevValue = prevProps.value;
    const { value } = this.props;
    const intValue = parseInt(value, 10);
    if (isInteger(prevValue) && isInteger(value) &&
         (this.incr(prevValue) === intValue ||
          this.decr(prevValue) === intValue)) {
      this.refs.input.select();
    }
  },

  incr(value) {
    const intValue = parseInt(value, 10);
    return intValue + this.props.step;
  },

  decr(value) {
    const intValue = parseInt(value, 10);
    return intValue - this.props.step;
  },

  handleIncr(value) {
    this.handleChange(String(this.incr(value)));
  },

  handleDecr(value) {
    if (value > this.props.min) {
      this.handleChange(String(this.decr(value)));
    }
  },

  handleChange(value) {
    this.props.onChange(this.props.name, value);
  },

  handleKeyDown(e) {
    const value = e.target.value;
    if (!isInteger(value) || (e.ctrlKey || e.altKey)) {
      return;
    }

    switch (e.keyCode) {
      case 38:  // UP
        e.preventDefault();
        this.handleIncr(value);
        break;
      case 40:  // DOWN
        e.preventDefault();
        this.handleDecr(value);
        break;
      default:
        break;
    }
  },

  handleBlur() {
    this.setState({ focus: false });
  },

  handleFocus() {
    this.setState({ focus: true });
  },

  handleMouseOver() {
    this.setState({ hover: true });
  },

  handleMouseOut() {
    this.setState({ hover: false });
  },

  render() {
    const { value } = this.props;
    const caretOpacity = (this.state.hover || this.state.focus) ? '1' : '0.2';

    const wrapperStyle = {
      position: 'relative',
      display: 'inline-block',
      marginLeft: '0.3em',
    };
    const caretWrapperStyle = {
      position: 'absolute',
      top: 0,
      left: '4em',
      width: '1em',
      height: '100%',
    };

    const baseStyle = {};
    if (isInteger(value)) {
      baseStyle.paddingRight = '0.8em';
    }
    const inputStyle = Object.assign({}, baseStyle, this.props.style);

    return (
      <div style={wrapperStyle}>
        <input
          id={`param-${this.props.name}`}
          onBlur={this.handleBlur}
          onChange={(e) => this.handleChange(e.target.value)}
          onFocus={this.handleFocus}
          onKeyDown={this.handleKeyDown}
          onMouseOver={this.handleMouseOver}
          onMouseOut={this.handleMouseOut}
          style={inputStyle}
          ref="input"
          tabIndex={this.props.tabIndex}
          type="text"
          value={value}
        />
      {isInteger(value) &&
        <div
          onMouseOver={this.handleMouseOver}
          onMouseOut={this.handleMouseOut}
          style={caretWrapperStyle}
        >
          <CaretButton
            onClick={() => this.handleIncr(value)}
            direction="up"
            style={{ padding: '0.3em 0.2em 0.1em', opacity: caretOpacity }}
            title="Increment value (Up)"
          />
          <CaretButton
            onClick={() => this.handleDecr(value)}
            direction="down"
            disabled={value <= this.props.min}
            style={{ padding: '0.1em 0.2em 0.3em', opacity: caretOpacity }}
            title="Decrement value (Down)"
          />
        </div>
      }
      </div>
    );
  },

});


export default PlurrInput;
