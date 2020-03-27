/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';

import PlurrInput from './PlurrInput';

// XXX: hard-coded tabIndex value that matches translation textarea's value.
// Allows jumping to parameters before skipping to the submission button.
const tabIndexValue = 10;

const PlurrParamsForm = React.createClass({
  propTypes: {
    onChange: React.PropTypes.func.isRequired,
    params: React.PropTypes.object.isRequired,
  },

  contextTypes: {
    currentLocaleDir: React.PropTypes.string,
  },

  render() {
    const { params } = this.props;
    const style = {
      keyLabel: {
        color: '#326c80',
      },
      keyInput: {
        boxSizing: 'border-box',
        margin: '0',
        width: '5em',
      },
      paramsContainer: {
        margin: '0.5em 0.5em 0',
        textAlign: this.context.currentLocaleDir === 'ltr' ? 'left' : 'right',
      },
      inputWrapper: {
        display: 'inline-block',
        [`margin${
          this.context.currentLocaleDir === 'ltr' ? 'Right' : 'Left'
        }`]: '1.5em',
        marginBottom: '0.5em',
      },
    };

    return (
      <div style={style.paramsContainer}>
        {Object.keys(params).map((key, i) => (
          <div key={i} style={style.inputWrapper}>
            <label htmlFor={`param-${key}`} style={style.keyLabel}>
              {key}:
            </label>
            <PlurrInput
              name={key}
              onChange={this.props.onChange}
              style={style.keyInput}
              tabIndex={tabIndexValue}
              value={params[key]}
            />
          </div>
        ))}
      </div>
    );
  },
});

export default PlurrParamsForm;
