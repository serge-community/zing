/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';

import { highlightRO } from '../../../utils';


const PlurrPreviewOutput = React.createClass({

  propTypes: {
    errorMsg: React.PropTypes.string.isRequired,
    value: React.PropTypes.string.isRequired,
  },

  contextTypes: {
    currentLocaleCode: React.PropTypes.string,
    currentLocaleDir: React.PropTypes.string,
  },

  render() {
    const style = {
      itemBlock: {
        marginTop: '-0.5em',
        padding: '0.75em 0.5em',
        fontFamily: '"Raw", sans-serif',
      },
    };

    let { currentLocaleDir } = this.context;
    let { currentLocaleCode } = this.context;

    let output;
    if (this.props.value === '') {
      style.itemBlock.fontStyle = 'italic';

      currentLocaleDir = 'ltr';
      currentLocaleCode = 'en';

      if (this.props.errorMsg) {
        style.itemBlock.color = '#c30';
        output = this.props.errorMsg;
        if (this.context.currentLocaleDir === 'rtl') {
          style.itemBlock.marginTop = '1.5em';
        }
      } else {
        style.itemBlock.color = '#999';
        output = 'Please enter placeholder values above to see the rendered message.';
      }
    } else {
      output = highlightRO(this.props.value);
    }

    return (
      <div
        className="live-preview-output"
        style={style.itemBlock}
      >
        <div
          dir={currentLocaleDir}
          lang={currentLocaleCode}
          dangerouslySetInnerHTML={{ __html: output }}
        />
      </div>
    );
  },

});


export default PlurrPreviewOutput;
