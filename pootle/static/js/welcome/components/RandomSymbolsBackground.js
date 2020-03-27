/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';

import './RandomSymbolsBackground.css';

// Note that depending on your IDE/Editor,
// some symbols in the string below may appear as blank
// or tofu ones; they are in fact legitimate different
// symbols that modern browsers can render just fine
const symbols =
  'ABCFGHJKQRSTWXYZjmgpmĂĘŠŸƵǮбБГДёжЙФЩЪЮЯ' +
  'ÇØßÆÄÃÛÜÐÑΣΘΞΨΩΪαβγωϢϪξԹՃשאتيऄऴআঞਆੴ' +
  'ઊணஜఱఫฬง༖ဋႴႵᏤᎺぁじぢツポ㑈㓗㒲겅걚';

const numColors = 4;
const numChars = 200;
const fontSizeVariation = 20; // px
const minFontSize = 30; // px
const opacityVariation = 0.3; // 0..1
const minOpacity = 0.2; // 0..1
const blurVariation = 5; // 0, 1, 2, ...
const minBlur = 2; // 0, 1, 2, ...

class RandomSymbolsBackground extends React.Component {
  static propTypes() {
    return {
      items: React.PropTypes.array.isRequired,
    };
  }

  static shouldComponentUpdate() {
    return false;
  }

  render() {
    const items = [];

    const maxSymIdx = symbols.length - 1;
    for (let i = 0; i < numChars; i++) {
      const char = symbols.charAt(Math.round(Math.random() * maxSymIdx));
      const left = Math.random() * 100;
      const top = Math.random() * 100;
      const depth = Math.random();
      const fontSize = depth * fontSizeVariation + minFontSize;
      const color = Math.round(Math.random() * (numColors - 1));
      const opacity = depth * opacityVariation + minOpacity;
      const blur = Math.round((1 - depth) * blurVariation) + minBlur;

      const style = {
        left: `${left}%`,
        top: `${top}%`,
        fontSize: `${fontSize}px`,
        opacity,
        WebkitFilter: `blur(${blur}px)`,
      };

      items.push(
        <i key={i} className={`c${color}`} style={style}>
          {char}
        </i>
      );
    }

    return <div className="random-symbols-background-component">{items}</div>;
  }
}

export default RandomSymbolsBackground;
