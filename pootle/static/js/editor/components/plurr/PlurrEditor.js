/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import Plurr from 'plurr';
import React from 'react';

import RawFontTextarea from '../RawFontTextarea';
import PlurrPreview from './PlurrPreview';


const paramsCache = {

  cacheKey: 'plurrParamsCache',

  get(key = null) {
    const cache = JSON.parse(localStorage.getItem(this.cacheKey)) || {};

    if (key !== null) {
      return cache[key] || '';
    }

    return cache;
  },

  set(key, value) {
    const currentCache = this.get();
    const newCache = Object.assign({}, currentCache, { [key]: value });
    localStorage.setItem(this.cacheKey, JSON.stringify(newCache));
  },

};


const PlurrEditor = React.createClass({

  propTypes: {
    autoFocus: React.PropTypes.bool,
    initialValue: React.PropTypes.string,
    isDisabled: React.PropTypes.bool,
    onChange: React.PropTypes.func.isRequired,
    value: React.PropTypes.string.isRequired,
  },

  contextTypes: {
    currentLocaleCode: React.PropTypes.string,
  },

  getInitialState() {
    return {
      params: {},
    };
  },

  componentWillMount() {
    this.plurr = new Plurr({ locale: this.context.currentLocaleCode });
  },

  componentWillUnMount() {
    this.plurr = null;
  },

  extractParamsFrom(value) {
    const params = {};
    let exception = null;

    try {
      const opts = {
        locale: this.context.currentLocaleCode,
        strict: false,
        callback: (name) => {
          if (name) {
            params[name] = paramsCache.get(name);
            return params[name];
          }
          return '';
        },
      };
      this.plurr.format(value, {}, opts);
    } catch (e) {
      exception = e;
    }

    return [params, exception];
  },

  handleParamChange(key, value) {
    const params = Object.assign({}, this.state.params, { [key]: value });
    paramsCache.set(key, value);
    this.setState({ params });
  },

  render() {
    const { value } = this.props;
    const [params, exception] = this.extractParamsFrom(value);

    const hasParams = Object.keys(params).length > 0;
    const hasAllValues = Object.keys(params).reduce(
      (state, key) => state && paramsCache.get(key) !== '',
      true
    );

    // Not using `null` because prop validation would fail (facebook/react#2166)
    let renderedValue = '';
    let errorMsg = exception !== null ? exception.message : '';

    if (!errorMsg && hasAllValues) {
      try {
        // Plurr mutates the params object, let's pass a copy around to avoid
        // unexpected rendering surprises (Plurr#10)
        const paramsCopy = Object.assign({}, params);
        renderedValue = this.plurr.format(value, paramsCopy,
                                          { locale: this.context.currentLocaleCode });
      } catch (e) {
        errorMsg = e.message;
      }
    }

    const style = {
      textarea: {
        border: '0px',
        outline: 'none',
        resize: 'none',
        margin: '0',
      },
    };

    const shouldDisplayPreview = errorMsg || hasParams;

    return (
      <div>
        <RawFontTextarea
          autoFocus={this.props.autoFocus}
          initialValue={this.props.initialValue}
          isDisabled={this.props.isDisabled}
          onChange={this.props.onChange}
          style={style.textarea}
        />
      {shouldDisplayPreview &&
        <PlurrPreview
          errorMsg={errorMsg}
          onChange={this.handleParamChange}
          params={params}
          value={renderedValue}
        />
      }
      </div>
    );
  },

});


export default PlurrEditor;
