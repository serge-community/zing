/*
 * Copyright (C) Pootle contributors.
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import $ from 'jquery';

import { formatTimeDelta } from 'utils/time';


const helpers = {

  /* Updates relative dates */
  updateRelativeDates() {
    $('.js-relative-date').each((i, e) => {
      $(e).text(
        formatTimeDelta(Date.parse($(e).attr('datetime'), { addDirection: true }))
      );
    });
  },

};


export default helpers;
