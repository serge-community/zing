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


function updateInputState($checkboxes, $input) {
  if ($checkboxes.length === $checkboxes.filter(':checked').length) {
    $input.prop('disabled', false);
  } else {
    $input.prop('disabled', true);
  }
}


const helpers = {

  /* Updates relative dates */
  updateRelativeDates() {
    $('.js-relative-date').each((i, e) => {
      $(e).text(
        formatTimeDelta(Date.parse($(e).attr('datetime'), { addDirection: true }))
      );
    });
  },

  /* Updates the disabled state of an input button according to the
   * checked status of input checkboxes.
   */
  updateInputState(checkboxSelector, inputSelector) {
    const $checkbox = $(checkboxSelector);
    if ($checkbox.length) {
      const $input = $(inputSelector);
      updateInputState($checkbox, $input);
      $checkbox.change(() => {
        updateInputState($checkbox, $input);
      });
    }
  },

};


export default helpers;
