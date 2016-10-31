/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';
import { showModal } from './Modal';
import { t, tct } from 'utils/i18n';

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
        {tct('Keyboard Help (press %(kbdF1)s or %(kbdQuestion)s to open it again)', {
          kbdF1: <kbd>F1</kbd>,
          kbdQuestion: <kbd>?</kbd>,
        })}
      </span>,
    children: <HelpDialogContent />,
    className: 'keyboard-help-dialog-component',
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
    const spaceKey = <kbd>Space</kbd>;
    const or = <div className="or">{t('or')}</div>;

    return (
      <div>
        <div className="column">

          <div className="section">{t('Editor')}</div>

          <table>
            <tbody>
            <tr>
              <td>{t('Previous unit')}</td>
              <td>
                {modKey}<kbd>&uarr;</kbd>
                {or}
                {ctrlKey}<kbd>,</kbd>
              </td>
            </tr>
            <tr>
              <td>{t('Next unit')}</td>
              <td>
                {modKey}<kbd>&darr;</kbd>
                {or}
                {ctrlKey}<kbd>.</kbd>
              </td>
            </tr>
            <tr>
              <td>{t('Submit/suggest + go to next unit')}</td>
              <td>{modKey}{enterKey}</td>
            </tr>
            <tr>
              <td>{t('Toggle submit/suggest mode')}</td>
              <td>{modKey}{shiftKey}{spaceKey}</td>
            </tr>
            <tr>
              <td>{t('Toggle "Needs work"')}</td>
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

          <div className="section">{t('General')}</div>

          <table>
            <tbody>
              <tr>
                <td>{t('Close any dialog')}</td>
                <td>
                  <kbd>Esc</kbd>
                </td>
              </tr>
              <tr>
                <td>{t('Search')}</td>
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
