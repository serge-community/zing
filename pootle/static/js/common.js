/*
 * Copyright (C) Pootle contributors.
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import $ from 'jquery';
import 'jquery-magnific-popup';
import 'jquery-select2';
import 'jquery-tipsy';
import Spinner from 'spin';

import { q } from 'utils/dom';

import React from 'react';
import ReactDOM from 'react-dom';
import Avatar from 'components/Avatar';
import { showAboutDialog } from './shared/components/AboutDialog';
import { showKeyboardHelpDialog } from './shared/components/KeyboardHelpDialog';
import Hero from './welcome/components/Hero';

import cookie from 'utils/cookie';
import diff from 'utils/diff';
import mousetrap from 'mousetrap';

import agreement from './agreement';
import auth from './auth';
import browser from './browser';
import contact from './contact';
import dropdown from './dropdown';
import score from './score';
import search from './search';
import stats from './stats';
import configureStore from './store';
import utils from './utils';

Spinner.defaults = {
  lines: 11,
  length: 2,
  width: 5,
  radius: 11,
  rotate: 0,
  corners: 1,
  color: '#000',
  direction: 1,
  speed: 1,
  trail: 50,
  opacity: 1 / 4,
  fps: 20,
  zIndex: 2e9,
  className: 'spinner',
  top: 'auto',
  left: 'auto',
  position: 'relative',
};

// Pootle-specifics. These need to be kept here until:
// 1. they evolve into apps of their own
// 2. they're only used directly as modules from other apps (and they are
//    not referenced like `PTL.<module>.<method>`)

window.PTL = window.PTL || {};

PTL.auth = auth;
PTL.agreement = agreement;
PTL.contact = contact;
PTL.dropdown = dropdown;
PTL.score = score;
PTL.search = search;
PTL.stats = stats;
PTL.utils = utils;
PTL.utils.diff = diff;

PTL.store = configureStore();

PTL.common = {
  init(opts) {
    PTL.auth.init();
    browser.init();

    // Tipsy setup
    $(document).tipsy({
      gravity: $.fn.tipsy.autoBounds2(150, 'n'),
      html: true,
      fade: true,
      delayIn: 750,
      opacity: 1,
      live: '[title], [original-title]',
    });
    setInterval($.fn.tipsy.revalidate, 1000);

    $('.js-select2').select2({
      width: 'resolve',
    });

    // Set CSRF token for XHR requests (jQuery-specific)
    $.ajaxSetup({
      traditional: true,
      crossDomain: false,
      beforeSend(xhr, settings) {
        // Set CSRF token only for local requests.
        if (
          !this.crossDomain &&
          !/^(GET|HEAD|OPTIONS|TRACE)$/.test(settings.type)
        ) {
          xhr.setRequestHeader('X-CSRFToken', cookie('csrftoken'));
        }
      },
    });

    /* Popups */
    $(document).magnificPopup({
      type: 'ajax',
      delegate: '.js-popup-ajax',
      mainClass: 'popup-ajax',
    });

    $(document).on('click', '.js-about-link', (e) => {
      e.preventDefault();
      showAboutDialog();
    });

    /* Bind hotkeys */
    const hotkeys = mousetrap(document.body);

    hotkeys.stopCallback = (e, element, combo) => {
      if (combo !== '?') {
        return false;
      }

      // stop for input, select and textarea
      return (
        element.tagName === 'INPUT' ||
        element.tagName === 'SELECT' ||
        element.tagName === 'TEXTAREA'
      );
    };

    hotkeys.bind(['f1', '?'], (e) => {
      e.preventDefault();
      showKeyboardHelpDialog();
    });

    /* Setup React components */

    if (q('#js-navbar-avatar') !== null) {
      ReactDOM.render(
        <Avatar size={24} tagName="span" {...opts.user} />,
        q('#js-navbar-avatar')
      );
    }

    if (q('.js-welcome-hero') !== null) {
      ReactDOM.render(<Hero />, q('.js-welcome-hero'));
    }
  },
};
