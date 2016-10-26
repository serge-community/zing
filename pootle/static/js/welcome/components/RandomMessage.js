/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';


// passed `items` prop is an array, where each element should be either
// an array [message, lang], or a simple message (string or Node)
class RandomMessage extends React.Component {

  static propTypes() {
    return {
      items: React.PropTypes.array.isRequired,
    };
  }

  static shouldComponentUpdate() {
    return false;
  }

  render() {
    const idx = Math.round(Math.random() * (this.props.items.length - 1));
    let item = this.props.items[idx];
    item = Array.isArray(item) ? {
      message: item[0],
      lang: item[1],
    } : {
      message: item,
    };

    return (
      <span
        className="random-message-component"
        lang={item.lang}
      >{item.message}</span>
    );
  }

}


export default RandomMessage;
