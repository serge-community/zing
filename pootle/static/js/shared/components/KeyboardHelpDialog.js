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


export function showKeyboardHelpDialog() {
  showModal({
    title:
      <span>
        Keyboard Help (press <kbd>F1</kbd> or <kbd>?</kbd> to open;
        press <kbd>Esc</kbd> to close)
      </span>,
    children: <HelpDialogContent />,
    className: 'KeyboardHelpDialog',
  });
}


const HelpDialogContent = React.createClass({

  render() {
    const macOS = navigator.platform.indexOf('Mac') === 0;

    const modKey = macOS ? <kbd className="clover" /> : <kbd>Ctrl</kbd>;
    const ctrlKey = macOS ? <kbd>Control</kbd> : <kbd>Ctrl</kbd>;
    const shiftKey = <kbd>Shift</kbd>;
    const enterKey = <kbd>Enter</kbd>;
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
            <tr>
              <td>Toggle submit/suggest mode</td>
              <td>{modKey}{shiftKey}{spaceKey}</td>
            </tr>
            <tr>
              <td>Toggle "Needs work"</td>
              <td>
                {modKey}<kbd>/</kbd>
                {or}
                {ctrlKey}{spaceKey}
              </td>
            </tr>
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
