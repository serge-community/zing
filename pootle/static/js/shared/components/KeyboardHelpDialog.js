/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';
import { showModal } from './Modal';

import './KeyboardHelpDialog.css';

let keyboardHelpOpen = false;

export function showKeyboardHelpDialog() {
  if (keyboardHelpOpen) {
    return;
  }

  keyboardHelpOpen = true;
  showModal({
    title:
      <span>
        Keyboard Help (press <kbd>F1</kbd> to open;
        press <kbd>Esc</kbd> to close)
      </span>,
    children: <HelpDialogContent />,
    className: 'KeyboardHelpDialog',
    onClose: () => { keyboardHelpOpen = false; },
  });
}

const HelpDialogContent = React.createClass({

  render() {
    const macOS = navigator.platform.indexOf('Mac') === 0;

    const modKey = macOS ? <kbd className="clover" /> : <kbd>Ctrl</kbd>;
    const ctrlKey = macOS ? <kbd>Control</kbd> : <kbd>Ctrl</kbd>;
    const shiftKey = <kbd>Shift</kbd>;
    const enterKey = <kbd>Enter</kbd>;
    /* const escKey = <kbd>Esc</kbd>; */
    const spaceKey = <kbd>Space</kbd>;
    const or = <div className="or">or</div>;

    return (
      <div>
        <div className="column">

          <div className="section">Editor</div>

          <table>
            <tbody>
            <tr>
              <td>Previous unit</td>
              <td>
                {modKey}<kbd>&uarr;</kbd>
                {or}
                {ctrlKey}<kbd>,</kbd>
              </td>
            </tr>
            <tr>
              <td>Next unit</td>
              <td>
                {modKey}<kbd>&darr;</kbd>
                {or}
                {ctrlKey}<kbd>.</kbd>
              </td>
            </tr>
            <tr>
              <td>Submit/suggest + go to next unit</td>
              <td>{modKey}{enterKey}</td>
            </tr>
            {/*
            <tr>
              <td>Submit/suggest + stay</td>
              <td>{modKey}{shiftKey}{enterKey}</td>
            </tr>
            */}
            <tr>
              <td>Toggle submit/suggest mode</td>
              <td>{modKey}{shiftKey}{spaceKey}</td>
            </tr>
            {/*
            <tr>
              <td>Mute all critical checks</td>
              <td>{modKey}{shiftKey}<kbd>M</kbd></td>
            </tr>
             */}
            <tr>
              <td>Toggle "Needs work"</td>
              <td>
                {modKey}<kbd>/</kbd>
                {or}
                {ctrlKey}{spaceKey}
              </td>
            </tr>
            {/*
            <tr>
              <td>Copy from source<br />(repeat for alt languages)</td>
              <td>{escKey}, then {spaceKey}</td>
            </tr>
            <tr>
              <td>Pretranslate using MT</td>
              <td>{escKey}, then {enterKey}</td>
            </tr>
            <tr>
              <td>Reset to current translation</td>
              <td>{escKey}, then <kbd>Backspace</kbd></td>
            </tr>
            <tr>
              <td>Toggle raw mode</td>
              <td>{ctrlKey}, then {ctrlKey}</td>
            </tr>
            <tr>
              <td>Select previous placeable</td>
              <td><kbd>Alt</kbd>{shiftKey}<kbd>&larr;</kbd></td>
            </tr>
            <tr>
              <td>Select next placeable</td>
              <td><kbd>Alt</kbd>{shiftKey}<kbd>&rarr;</kbd></td>
            </tr>
            <tr>
              <td>Copy placeable into the editor</td>
              <td><kbd>Alt</kbd>{shiftKey}<kbd>&darr;</kbd></td>
            </tr>
            */}
            </tbody>
          </table>
        </div>

        <div className="column">

          <div className="section">General:</div>

          <table>
            <tbody>
              <tr>
                <td>Search</td>
                <td>
                  {modKey}{shiftKey}<kbd>S</kbd>
                  {or}
                  {ctrlKey}<kbd>{'`'}</kbd>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    );
  },

});
