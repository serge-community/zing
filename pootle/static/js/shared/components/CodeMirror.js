/*
 * Copyright (C) Pootle contributors.
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';

import * as CM from 'codemirror';
import 'codemirror/addon/display/placeholder';
import 'codemirror/lib/codemirror.css';

import './CodeMirror.css';

const CodeMirror = React.createClass({
  propTypes: {
    mode: React.PropTypes.string.isRequired,
    // Temporarily needed to support submitting forms not controlled by JS
    name: React.PropTypes.string,
    onChange: React.PropTypes.func,
    placeholder: React.PropTypes.string,
    value: React.PropTypes.string,
  },

  componentDidMount() {
    const { mode } = this.props;

    this.codemirror = CM.fromTextArea(this.refs.editor, {
      mode,
      lineWrapping: true,
    });

    this.codemirror.on('change', this.handleChange);
  },

  handleChange() {
    if (this.props.onChange) {
      this.props.onChange(this.codemirror.getValue());
    }
  },

  render() {
    const extraProps = {};

    if (this.props.name) {
      extraProps.name = this.props.name;
    }

    return (
      <textarea
        defaultValue={this.props.value}
        placeholder={this.props.placeholder}
        ref="editor"
        {...extraProps}
      />
    );
  },
});

export default CodeMirror;
