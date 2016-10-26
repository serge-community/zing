/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';
import { showModal } from './Modal';

import './AboutDialog.css';

export function showAboutDialog() {
  showModal({
    title: 'About this translation server...',
    children: <AboutDialogContent />,
    className: 'about-dialog-component',
  });
}

const AboutDialogContent = React.createClass({

  render() {
    return (
      <div>
        <div className="side-column">
          <img src="/static/images/logo.svg" />
        </div>
        <div className="main-content">
          <h1>Zing</h1>

          <p>
            This server is powered by <strong>Zing</strong> —
            online translation software developed by
            {' '}<a href="https://evernote.com/">Evernote</a>{' '}
            and based on open-source
            {' '}<a href="http://pootle.translatehouse.org/">Pootle</a>{' '}
            project.
          </p>

          <p>
            Source code and bug tracker:
            {' '}<a href="https://github.com/evernote/zing">Github</a>
          </p>

          <p className="copyright">
            © 2016 Pootle Contributors<br />
            © 2016 Zing Contributors
          </p>
        </div>
      </div>
    );
  },

});
