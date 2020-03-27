/*
 * Copyright (C) Pootle contributors.
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import autosize from 'autosize';
import React from 'react';

const AutosizeTextarea = React.createClass({
  componentDidMount() {
    autosize(this.refs.textarea);
  },

  componentDidUpdate() {
    autosize.update(this.refs.textarea);
  },

  componentWillUnmount() {
    autosize.destroy(this.refs.textarea);
  },

  render() {
    return <textarea ref="textarea" {...this.props} />;
  },
});

export default AutosizeTextarea;
