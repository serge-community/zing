/*
 * Copyright (C) Pootle contributors.
 *
 * This file is a part of the Pootle project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React, { PropTypes } from 'react';
import { PureRenderMixin } from 'react-addons-pure-render-mixin';
import AutoIcon from './AutoIcon';

const Avatar = React.createClass({

  // FIXME: be smarter with props validation, e.g. `email` should be required if
  // `src` is missing etc.
  propTypes: {
    tagName: PropTypes.string,
    email: PropTypes.string,
    displayName: PropTypes.string,
    size: PropTypes.number,
    src: PropTypes.string,
    username: PropTypes.string,
  },

  mixins: [PureRenderMixin],

  getDefaultProps() {
    return {
      tagName: 'a',
      size: 20,
    };
  },

  render() {
    const { email } = this.props;
    const { displayName } = this.props;
    const { size } = this.props;
    const { username } = this.props;

    const title = displayName || username;

    const pixelRatio = window.devicePixelRatio || 1;

    let icon = null;
    if (email) {
      const urlPrefix = 'https://secure.gravatar.com/avatar/';
      const src = `${urlPrefix}${email}?s=${size * pixelRatio}&d=blank`;
      icon = (
        <img
          src={src}
          title={title}
          width={size}
          height={size}
        />
      );
    }

    const style = {
      width: size,
      height: size,
    };

    const TagName = this.props.tagName;

    const attrs = TagName === 'a' ? {
      href: l(`/user/${username}/`),
    } : {};

    if (username !== undefined) {
      return (
        <TagName className="avatar" {...attrs}>
          <span className="avatar-image" style={style}>
            <AutoIcon
              mode="outline"
              size={size}
              lightness={50}
              saturation={50}
              title={title}
            />
            {icon}
          </span>
          <span className="user-name" title={username}>{title}</span>
        </TagName>
      );
    }

    return (
      <TagName className="avatar">
        <span className="avatar-image" style={style}>
          {icon}
        </span>
      </TagName>
    );
  },

});


export default Avatar;
