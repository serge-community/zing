/*
 * Copyright (C) Pootle contributors.
 *
 * This file is a part of the Pootle project. It is distributed under the GPL3
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
    // Seems we're hitting the bug in Firefox under Windows:
    // https://bugzilla.mozilla.org/show_bug.cgi?id=889376
    // (autosize.js tries to run the cleanup by dispatching
    // an event, and if our dom node is detached,
    // Firefox throws the NS_ERROR_UNEXPECTED error).
    // Until this is fixed in Autosize, we wrap the call to
    // autosize.destroy() with try..catch
    try {
      autosize.destroy(this.refs.textarea);
    } catch (err) {
      if (err.name === 'NS_ERROR_UNEXPECTED') {
        return;
      }
      throw err;
    }
  },

  render() {
    return (
      <textarea
        ref="textarea"
        {...this.props}
      />
    );
  },

});


export default AutosizeTextarea;
