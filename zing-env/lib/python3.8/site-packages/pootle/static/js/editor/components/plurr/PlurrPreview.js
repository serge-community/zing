/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';

import PlurrHelp from './PlurrHelp';
import PlurrParamsForm from './PlurrParamsForm';
import PlurrPreviewOutput from './PlurrPreviewOutput';


const PlurrPreview = React.createClass({

  propTypes: {
    errorMsg: React.PropTypes.string.isRequired,
    onChange: React.PropTypes.func.isRequired,
    params: React.PropTypes.object.isRequired,
    value: React.PropTypes.string.isRequired,
  },

  render() {
    const style = {
      previewBlock: {
        position: 'relative',
        backgroundColor: '#f6f6f6',
        color: '#666',
        borderTop: '1px solid rgba(0, 0, 0, 0.05)',
        fontSize: '115%',
      },
    };

    return (
      <div style={style.previewBlock}>
        <PlurrHelp />
        <PlurrParamsForm
          onChange={this.props.onChange}
          params={this.props.params}
        />
        <PlurrPreviewOutput
          errorMsg={this.props.errorMsg}
          value={this.props.value}
        />
      </div>
    );
  },

});


export default PlurrPreview;
