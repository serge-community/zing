/*
 * Copyright (C) Pootle contributors.
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';

import { outerHeight } from 'utils/dimensions';
import { q, qAll } from 'utils/dom';

import ContentEditor from './ContentEditor';
import ContentPreview from './ContentPreview';

import './LiveEditor.css';

const SPLIT_WIDTH = 1600;
const CONTENT_MARGIN = 30; // ~1.5em+
const WRAPPER_MARGIN = 40; // ~2em

export const LiveEditor = React.createClass({
  propTypes: {
    // Temporarily needed to support submitting forms not controlled by JS
    name: React.PropTypes.string.isRequired,
    initialValue: React.PropTypes.string.isRequired,
  },

  getInitialState() {
    return {
      value: this.props.initialValue,
    };
  },

  componentWillMount() {
    this.updateDimensions();
  },

  componentDidMount() {
    window.addEventListener('resize', this.updateDimensions);
  },

  componentWillUnmount() {
    window.removeEventListener('resize', this.updateDimensions);
  },

  getContentHeight() {
    const topHeight = outerHeight(q('#navbar')) + outerHeight(q('#header-tabs'));

    const formFields = qAll('.js-staticpage-non-content');
    const fieldsHeight = formFields.reduce(
      (total, fieldEl) => total + outerHeight(fieldEl),
      0
    );

    const usedHeight = topHeight + fieldsHeight + WRAPPER_MARGIN;
    const contentHeight = this.state.height - usedHeight;

    // Actual size is divided by two in the horizontal split
    if (this.state.width <= SPLIT_WIDTH) {
      return (contentHeight - CONTENT_MARGIN) / 2;
    }

    return contentHeight;
  },

  updateDimensions() {
    // FIXME: this can perfectly be part of the single state atom, and be
    // available to any component needing it via context.
    this.setState({
      height: window.innerHeight,
      width: window.innerWidth,
    });
  },

  handleChange(newValue) {
    this.setState({ value: newValue });
  },

  render() {
    const { value } = this.state;
    const contentHeight = Math.max(100, this.getContentHeight());
    const contentStyle = {
      height: contentHeight,
      minHeight: contentHeight, // Required for Firefox
      maxHeight: contentHeight, // Required for Firefox
    };

    return (
      <div className="live-editor">
        <ContentEditor
          name={this.props.name}
          onChange={this.handleChange}
          style={contentStyle}
          value={value}
        />
        <ContentPreview style={contentStyle} value={value} />
      </div>
    );
  },
});

export default LiveEditor;
