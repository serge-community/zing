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

import './AboutDialog.css';

export function showAboutDialog() {
  showModal({
    title: t('About this translation server...'),
    children: <AboutDialogContent />,
    className: 'about-dialog-component',
  });
}

const AboutDialogContent = React.createClass({
  render() {
    return (
      <div>
        <div className="side-column">
          <img src={s('images/logo.svg')} />
        </div>
        <div className="main-content">
          <h1>Zing</h1>

          <p>
            {tct(
              'This server is powered by %(zing)s — ' +
                'online translation software developed by %(evernoteLink)s ' +
                'and based on open-source %(pootleLink)s project.',
              {
                zing: <strong>Zing</strong>,
                evernoteLink: <a href="https://evernote.com/">Evernote</a>,
                pootleLink: <a href="http://pootle.translatehouse.org/">Pootle</a>,
              }
            )}
          </p>

          <p>
            {tct('Source code and bug tracker: %(githubLink)s', {
              githubLink: <a href="https://github.com/evernote/zing">GitHub</a>,
            })}
          </p>

          <p className="copyright">
            {t('© %(year)s Zing Contributors', { year: 2016 })}
            <br />
            {t('© 2016 Pootle Contributors')}
          </p>
        </div>
      </div>
    );
  },
});
