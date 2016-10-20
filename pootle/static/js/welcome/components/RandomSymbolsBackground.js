/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';
import ReactDOM from 'react-dom';

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

  componentDidMount() {
    const container = ReactDOM.findDOMNode(this);
    const maxSymIdx = symbols.length - 1;
    for (let i = 0; i < numChars; i ++) {
      const char = symbols.charAt(Math.round(Math.random() * maxSymIdx));
      const left = Math.random() * 100;
      const top = Math.random() * 100;
      const depth = Math.random();
      const fontSize = (depth * fontSizeVariation + minFontSize);
      const color = Math.round(Math.random() * (numColors - 1));
      const opacity = (depth * opacityVariation + minOpacity);
      const blur = Math.round((1 - depth) * blurVariation) + minBlur;

      const el = document.createElement('i');
      el.innerText = char;
      el.className = `c${color}`;
      el.style.left = `${left}%`;
      el.style.top = `${top}%`;
      el.style.fontSize = `${fontSize}px`;
      el.style.opacity = opacity;
      el.style.webkitFilter = `blur(${blur}px)`;
      container.appendChild(el);
    }
  }

  render() {
    return (
      <div className="RandomSymbolsBackground" />
    );
  }

}


export default RandomSymbolsBackground;
