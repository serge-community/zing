/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';

import './Dropdown.css';


const propTypes = {
  children: React.PropTypes.node.isRequired,
  isOpen: React.PropTypes.bool,
  onToggle: React.PropTypes.func.isRequired,
  tag: React.PropTypes.oneOfType([
    React.PropTypes.func,
    React.PropTypes.string,
  ]),
};

const defaultProps = {
  isOpen: false,
  tag: 'div',
};

const childContextTypes = {
  onMenuMouseDown: React.PropTypes.func.isRequired,
  onMenuMouseUp: React.PropTypes.func.isRequired,
  isOpen: React.PropTypes.bool.isRequired,
  onToggle: React.PropTypes.func.isRequired,
};


class Dropdown extends React.Component {

  constructor(props) {
    super(props);

    this.clickedInside = false;
    this.clickTimeout = null;

    this.handleKeyDown = this.handleKeyDown.bind(this);
    this.handleDocClick = this.handleDocClick.bind(this);
  }

  getChildContext() {
    return {
      onMenuMouseDown: this.handleMenuMouseDown.bind(this),
      onMenuMouseUp: this.handleMenuMouseUp.bind(this),
      isOpen: this.props.isOpen,
      onToggle: this.props.onToggle,
    };
  }

  componentDidUpdate(prevProps) {
    if (!prevProps.isOpen && this.props.isOpen) {
      document.addEventListener('keydown', this.handleKeyDown);
      document.addEventListener('click', this.handleDocClick);
    }
    if (prevProps.isOpen && !this.props.isOpen) {
      document.removeEventListener('keydown', this.handleKeyDown);
      document.removeEventListener('click', this.handleDocClick);
    }
  }

  componentWillUnmount() {
    clearTimeout(this.clickTimeout);
    document.removeEventListener('keydown', this.handleKeyDown);
    document.removeEventListener('click', this.handleDocClick);
  }

  handleDocClick(e) {
    if (this.clickedInside) {
      return;
    }

    this.props.onToggle(e);
  }

  handleKeyDown(e) {
    if (e.key === 'Escape') {
      this.props.onToggle(e);
    }
  }

  handleMenuMouseDown() {
    this.clickedInside = true;
  }

  handleMenuMouseUp() {
    this.clickTimeout = setTimeout(() => {
      this.clickedInside = false;
    }, 0);
  }

  render() {
    const Tag = this.props.tag;

    return (
      <Tag
        className="dropdown-wrapper"
      >
        {this.props.children}
      </Tag>
    );
  }
}

Dropdown.propTypes = propTypes;
Dropdown.defaultProps = defaultProps;
Dropdown.childContextTypes = childContextTypes;


export default Dropdown;
