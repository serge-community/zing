/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';
import ReactDOM from 'react-dom';

import DueDateContainer from './components/DueDateContainer';

window.PTL = window.PTL || {};


PTL.duedates = {

  init(opts) {
    ReactDOM.render(
      <DueDateContainer initialDueDate={opts.dueDate} />,
      document.querySelector('.js-mnt-duedate-manage')
    );
  },

};
