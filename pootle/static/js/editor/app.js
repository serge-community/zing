/*
 * Copyright (C) Pootle contributors.
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import $ from 'jquery';
import _ from 'underscore';
import React from 'react';
import ReactDOM from 'react-dom';

import TimeSince from 'components/TimeSince';
import ReactRenderer from 'utils/ReactRenderer';

// jQuery plugins
import 'jquery-bidi';
import 'jquery-easing';
import 'jquery-highlightRegex';
import 'jquery-history';
import 'jquery-serializeObject';
import 'jquery-utils';

// Other plugins
import cx from 'classnames';
import Levenshtein from 'levenshtein';
import mousetrap from 'mousetrap';
import assign from 'object-assign';

import StatsAPI from 'api/StatsAPI';
import UnitAPI from 'api/UnitAPI';
import diff from 'utils/diff';
import { q, qAll } from 'utils/dom';
import fetch from 'utils/fetch';
import { nt, t } from 'utils/i18n';
import linkHashtags from 'utils/linkHashtags';
import UnitsList from './UnitsList';

import SuggestionFeedbackForm from './components/SuggestionFeedbackForm';
import UploadTimeSince from './components/UploadTimeSince';

import captcha from '../captcha';
import helpers from '../helpers';
import msg from '../msg';
import score from '../score';
import search from '../search';
import utils from '../utils';
import {
  decodeEntities, escapeUnsafeRegexSymbols, getAreaId, makeRegexForMultipleWords,
} from './utils';

import ReactEditor from './index';

// Make the react-based editor available to templates. Long term, `index` would
// be the actual entry point, entirely superseding the `app` module.
PTL.reactEditor = ReactEditor;

const ALLOWED_SORTS = ['oldest', 'newest', 'default'];
const SHOW_CONTEXT_ROWS_TIMEOUT = 200;

const filterSelectOpts = {
  dropdownAutoWidth: true,
  dropdownCssClass: 'checks-dropdown',
  width: 'off',
};
const sortSelectOpts = assign({
  minimumResultsForSearch: -1,
}, filterSelectOpts);


const mtProviders = [];


function highlightSuggestionsDiff(unit) {
  qAll('.js-suggestion-text').forEach(
    (translationTextNode) => {
      // eslint-disable-next-line no-param-reassign
      translationTextNode.innerHTML = diff(unit.targetText(),
                                           translationTextNode.dataset.string);
    }
  );
}


function _refreshChecksSnippet(newChecks) {
  const $checks = $('.js-unit-checks');
  const focusedArea = $('.focusthis')[0];

  $checks.html(newChecks).show();
  utils.blinkClass($checks, 'blink', 4, 200);
  focusedArea.focus();
}


window.PTL = window.PTL || {};


PTL.editor = {

  /* Initializes the editor */
  init(options) {
    /* Default settings */
    this.settings = {
      mt: [],
    };

    if (options) {
      assign(this.settings, options);
    }

    /* Cached elements */
    this.backToBrowserEl = q('.js-back-to-browser');
    this.$editorActivity = $('#js-editor-act');
    this.$viewRowsBefore = $('.js-view-rows-before');
    this.$contextRowsBefore = $('.js-context-rows-before');
    this.$editorRow = $('.js-editor-row');
    this.$viewRowsAfter = $('.js-view-rows-after');
    this.$contextRowsAfter = $('.js-context-rows-after');
    this.editorTableEl = q('.js-editor-table');
    this.$filterStatus = $('#js-filter-status');
    this.$filterChecks = $('#js-filter-checks');
    this.$filterChecksWrapper = $('.js-filter-checks-wrapper');
    this.$filterSortBy = $('#js-filter-sort');
    this.$navNext = $('#js-nav-next');
    this.$navPrev = $('#js-nav-prev');
    this.unitPositionEl = q('.js-unit-position');
    this.unitCountEl = q('.js-unit-count');

    /* Initialize variables */

    this.filter = 'all';
    this.checks = [];
    this.sortBy = 'default';
    this.modifiedSince = null;
    this.user = null;
    this.preventNavigation = false;
    this.units = new UnitsList();
    this.isUnitDirty = false;
    this.editorIsClosed = false;
    this.contextTimer = null;
    this.lastFilter = null;

    this.units.onUnitChange = (uid) => {
      this.handleUnitChange(uid);
    };

    this.units.onViewRowsChange = (uid) => {
      if (uid === this.units.uid) {
        this.handleViewRowsChange(uid);
      }
    };

    this.units.onContextData = (uid) => {
      if (uid === this.units.uid) {
        this.showContextRows();
      }
    };

    this.units.onEmptyResults = (/* reqData */) => {
      // TODO: discard if reqData doesn't match
      this.handleEmptyResults();
    };

    this.isLoading = true;
    this.showActivity();

    /* Levenshtein word comparer */
    this.wordComparer = new Levenshtein({ compare: 'words' });

    /* Compile templates */
    this.tmpl = {
      vUnit: _.template($('#view_unit').html()),
      tm: _.template($('#tm_suggestions').html()),
      msg: _.template($('#js-editor-msg').html()),
    };

    /* Initialize search */
    search.init({
      onSearch: this.onSearch,
    });

    /* Select2 */
    this.$filterStatus.select2(filterSelectOpts);
    this.$filterSortBy.select2(sortSelectOpts);

    /* Screenshot images */
    $('#editor').on('click', '.js-dev-img', function displayScreenshot(e) {
      e.preventDefault();

      $(this).magnificPopup({
        type: 'image',
        gallery: {
          enabled: true,
        },
      }).magnificPopup('open');
    });

    /*
     * Bind event handlers
     */

    /* Editor toolbar navigation/search/filtering */
    $('#toolbar').on('click', '#js-nav-prev', () => this.gotoPrev());
    $('#toolbar').on('click', '#js-nav-next', () => this.gotoNext());
    $('#toolbar').on('change', '#js-filter-sort', () => this.filterSort());

    /* Filtering */
    $('#actions').on('change', '#js-filter-status', () => this.filterStatus());
    $('#actions').on('change', '#js-filter-checks', () => this.filterChecks());

    /* State changes */
    $('#editor').on('change', 'input.fuzzycheck',
                   () => this.onStateChange());
    $('#editor').on('click', 'input.fuzzycheck',
                   () => this.onStateClick());
    $('#editor').on('input', '#id_translator_comment',
                   () => this.handleTranslationChange());

    /* Context row preview */
    $('#editor').on('mouseover', '.js-permalink', (e) => this.handlePermalinkMouseover(e));
    $('#editor').on('mouseout', '.js-permalink', (e) => this.handlePermalinkMouseout(e));

    /* Suggest / submit */
    $('#editor').on('click', '.switch-suggest-mode a',
                   (e) => this.toggleSuggestMode(e));

    /* Update focus when appropriate */
    $('#editor').on('focus', '.focusthis', (e) => {
      PTL.editor.focused = e.target;
    });
    $('#editor').on('focus', '.js-translation-area', (e) => {
      $(e.target).closest('.js-editor-area-wrapper').addClass('is-focused');
    });
    $('#editor').on('blur', '.js-translation-area', (e) => {
      $(e.target).closest('.js-editor-area-wrapper').removeClass('is-focused');
    });

    /* Write TM results, special chars... into the currently focused element */
    $('#editor').on('click', '.js-editor-copytext', (e) => this.copyText(e));
    $('#editor').on('click', '.js-editor-copy-tm-text', (e) => this.copyTMText(e));

    /* Copy translator comment */
    $('#editor').on('click', '.js-editor-copy-comment', (e) => {
      const text = e.currentTarget.dataset.string;
      this.copyComment(text);
    });

    /* Copy original translation */
    $('#editor').on('click', '.js-copyoriginal', (e) => {
      this.copyOriginal(e.currentTarget.dataset.languageCode);
    });

    /* Editor navigation/submission */
    $('#editor').on('mouseup', 'tr.view-row', this.gotoUnit);
    $('#editor').on('click', 'input.submit', (e) => {
      e.preventDefault();
      this.handleSubmit();
    });
    $('#editor').on('click', 'input.suggest', (e) => {
      e.preventDefault();
      this.handleSuggest();
    });
    $('#editor').on('click', '.js-suggestion-reject', (e) => {
      e.stopPropagation();
      this.rejectSuggestion(e.currentTarget.dataset.suggId);
    });
    $('#editor').on('click', '.js-suggestion-accept', (e) => {
      e.stopPropagation();
      this.acceptSuggestion(e.currentTarget.dataset.suggId);
    });
    $('#editor').on('click', '.js-suggestion-toggle',
      (e) => this.toggleSuggestion(e, { canHide: true }));

    if (this.settings.canReview) {
      $('#editor').on('click', '.js-user-suggestion',
        (e) => this.toggleSuggestion(e, { canHide: false }));
    }

    $('#editor').on('click', '.js-translate-lightbox', () => this.closeSuggestion());

    $('#editor').on('click', '#js-toggle-timeline', (e) => this.toggleTimeline(e));
    $('#editor').on('click', '.js-toggle-check', (e) => {
      this.toggleCheck(e.currentTarget.dataset.checkId);
    });

    /* Commenting */
    $('#editor').on('click', '.js-editor-comment', (e) => {
      e.preventDefault();
      const $elem = $('.js-editor-comment-form');
      const $comment = $('.js-editor-comment');
      $comment.toggleClass('selected');
      if ($comment.hasClass('selected')) {
        $elem.css('display', 'inline-block');
        $('#id_translator_comment').focus();
      } else {
        $elem.css('display', 'none');
      }
    });
    $('#editor').on('submit', '#js-comment-form', (e) => this.addComment(e));
    $('#editor').on('click', '.js-comment-remove', (e) => this.removeComment(e));

    /* Misc */
    $('#editor').on('click', '.js-toggle-raw', (e) => {
      e.preventDefault();
      $('.js-translate-translation').toggleClass('raw');
      const toggle = document.querySelector('.js-toggle-raw');
      toggle.classList.toggle('selected');
      ReactEditor.setProps({ isRawMode: toggle.classList.contains('selected') });
    });

    /* Confirmation prompt */
    window.addEventListener('beforeunload', (e) => {
      if (PTL.editor.isUnitDirty || PTL.editor.isSuggestionFeedbackFormDirty) {
        // eslint-disable-next-line no-param-reassign
        e.returnValue = gettext(
          'You have unsaved changes in this string. Navigating away will discard those changes.'
        );
      }
    });

    /* Bind hotkeys */
    const hotkeys = mousetrap(document.body);

    // FIXME: move binding to `SuggestionFeedbackForm` component
    hotkeys.bind('esc', (e) => {
      e.preventDefault();
      if (this.selectedSuggestionId !== undefined) {
        this.closeSuggestion();
        return;
      }
      this.hideContextRows();
    });
    // Leave 'ctrl+return' for backward compatibility with Mac
    hotkeys.bind(['mod+return', 'ctrl+return'], (e) => {
      e.preventDefault();
      if (this.isSuggestMode()) {
        this.handleSuggest();
      } else {
        this.handleSubmit();
      }
    });
    hotkeys.bind(['mod+/', 'ctrl+space'], (e) => {
      e.preventDefault();
      this.toggleState();
    });
    hotkeys.bind('ctrl+shift+space', (e) => {
      e.preventDefault();
      this.toggleSuggestMode(e);
    });

    hotkeys.bind(['mod+up', 'ctrl+,'], (e) => {
      e.preventDefault();
      this.gotoPrev();
    });
    hotkeys.bind(['mod+down', 'ctrl+.'], (e) => {
      e.preventDefault();
      this.gotoNext({ isSubmission: false });
    });

    if (navigator.platform.toUpperCase().indexOf('MAC') >= 0) {
      // Optimize string join with '<br/>' as separator
      this.$navNext.attr('title',
        gettext(
          'Go to the next string (Ctrl+.)<br/><br/>Also:<br/>Next page: ' +
          'Ctrl+Shift+.<br/>Last page: Ctrl+Shift+End'
        )
      );
      this.$navPrev.attr('title',
        gettext(
          'Go to the previous string (Ctrl+,)<br/><br/>Also:<br/>Previous page: ' +
          'Ctrl+Shift+,<br/>First page: Ctrl+Shift+Home'
        )
      );
    }

    /* XHR activity indicator */
    $(document).ajaxStart(() => {
      clearTimeout(this.delayedActivityTimer);
      if (this.isLoading) {
        return;
      }

      this.delayedActivityTimer = setTimeout(() => {
        this.showActivity();
      }, 3000);
    });
    $(document).ajaxStop(() => {
      clearTimeout(this.delayedActivityTimer);
      if (!this.isLoading) {
        this.hideActivity();
      }
    });

    /* Load MT providers */
    this.settings.mt.forEach((provider) => {
      require.ensure([], () => {
        // Retrieve actual module name: FOO_BAR_BAZ => FooBarBaz
        const moduleName = provider.name.split('_').map(
          (x) => x[0] + x.slice(1).toLowerCase()
        ).join('');
        // Webpack doesn't like template strings for now...
        // eslint-disable-next-line prefer-template
        const Module = require('./mt/providers/' + moduleName).default;
        mtProviders.push(new Module(provider.key));
      });
    });

    /* History support */
    $.history.init((hash) => {
      console.log('$.history.init(), hash:', hash);
      const params = utils.getParsedHash(hash);

      if (this.selectedSuggestionId !== undefined) {
        this.closeSuggestion({ checkIfCanNavigate: false });
      }

      // Walk through known filtering criteria and apply them to the editor object

      let uid;
      if (params.unit) {
        uid = parseInt(params.unit, 10);

        if (uid && !isNaN(uid)) {
          if (uid !== this.units.uid) {
            setTimeout(() => {
              this.units.goto(uid);
            }, 0);
          }
        }
      }

      // get filter criteria (hash without the 'unit' part)
      const filterHash = utils.updateHashPart(undefined, undefined, ['unit'], hash);
      if (filterHash === this.lastFilter) {
        // if filter criteria are the same, and units have already been loaded,
        // exit early...
        if (this.units.length > 0) {
          return;
        }
      }
      // ...otherwise, save the filter value for later comparison
      // continue through the filters
      // and prepare the query to download the units
      this.lastFilter = filterHash;
      console.log('Filter has changed, will reload view rows');

      // Reset to defaults
      this.filter = 'all';
      this.checks = [];
      this.category = undefined;
      this.sortBy = 'default';

      const filterName = params.filter || 'all';

      // Set current state
      this.filter = filterName;

      if (this.filter === 'checks') {
        if ('checks' in params) {
          this.checks = params.checks.split(',');
        } else if ('category' in params) {
          this.category = params.category;
        }
        this.getCheckOptions();
      }
      if ('sort' in params) {
        const { sort } = params;
        this.sortBy = ALLOWED_SORTS.indexOf(sort) !== -1 ? sort : 'default';
      }

      if ('modified-since' in params) {
        this.modifiedSince = params['modified-since'];
      } else {
        this.modifiedSince = null;
      }

      if ('month' in params) {
        this.month = params.month;
      } else {
        this.month = null;
      }

      // Only accept the user parameter for 'user-*' filters
      if ('user' in params && this.filter.indexOf('user-') === 0) {
        this.user = encodeURIComponent(params.user);
        const user = this.user;

        const values = {
          'user-suggestions':
            // Translators: '%s' is a username
            interpolate(gettext("%s's pending suggestions"), [user]),
          'user-suggestions-accepted':
            // Translators: '%s' is a username
            interpolate(gettext("%s's accepted suggestions"), [user]),
          'user-suggestions-rejected':
            // Translators: '%s' is a username
            interpolate(gettext("%s's rejected suggestions"), [user]),
          'user-submissions':
            // Translators: '%s' is a username
            interpolate(gettext("%s's submissions"), [user]),
          'user-submissions-overwritten':
            // Translators: '%s' is a username, meaning "submissions by %s,
            // that were overwritten"
            interpolate(gettext("%s's overwritten submissions"), [user]),
        };
        const newOpts = [];
        for (const key in values) {
          if (!values.hasOwnProperty(key)) {
            continue;
          }
          newOpts.push(`
            <option value="${key}" data-user="${user}" class="js-user-filter">
              ${values[key]}
            </option>
          `);
        }
        $('.js-user-filter').remove();
        this.$filterStatus.append(newOpts.join(''));
      }

      if ('search' in params) {
        // Note that currently the search, if provided along with the other
        // filters, would override them
        this.filter = 'search';

        const newState = {
          searchText: params.search,
        };

        if ('sfields' in params) {
          newState.searchFields = params.sfields.split(',');
        }
        if ('soptions' in params) {
          newState.searchOptions = params.soptions.split(',');
        }

        search.setState(newState);
      }

      // Update the filter UI to match the current filter

      // disable navigation on UI toolbar events to prevent data reload
      this.preventNavigation = true;

      const filterValue = this.filter === 'search' ? 'all' : this.filter;
      this.$filterStatus.select2('val', filterValue);

      if (this.filter === 'checks') {
        this.$filterChecksWrapper.css('display', 'inline-block');
        const selectedValue = this.category || this.checks[0] || 'all';
        this.$filterChecks.select2(filterSelectOpts).select2('val', selectedValue);
      } else {
        this.$filterChecksWrapper.hide();
      }

      this.$filterSortBy.select2('val', this.sortBy);

      // re-enable normal event handling
      this.preventNavigation = false;

      // get all the uids and see if the uId is in the list
      const reqData = {
        path: this.settings.pootlePath,
      };
      assign(reqData, this.getReqData());
      if (uid) {
        reqData.uid = uid;
      }
      this.units.fetchUids(reqData);
    }, { unescape: true });
  },

  /* Stuff to be done when the editor is ready  */
  ready() {
    if (this.units.unit.is_obsolete) {
      this.displayObsoleteMsg();
    }

    highlightSuggestionsDiff(this.units.unit);

    // set direction of the comment body
    $('.extra-item-comment').filter(':not([dir])').bidi();
    // set direction of the suggestion body
    $('.suggestion-translation').filter(':not([dir])').bidi();

    const $devComments = $('.js-developer-comments');
    $devComments.html(linkHashtags($devComments.html()));

    if (this.filter === 'search') {
      this.hlSearch();
    }

    if (this.settings.tmUrl !== '') {
      this.getTMUnits();
    }

    if (this.units.unit.tm_suggestions) {
      const tmContent = this.getTMUnitsContent(this.units.unit.tm_suggestions);
      $('#extras-container').append(tmContent);
    }

    this.runHooks();

    this.isUnitDirty = false;
    this.keepState = false;
    this.isLoading = false;
    this.hideActivity();
    this.updateExportLink();
    helpers.updateRelativeDates();
  },

  canNavigate() {
    if (this.isUnitDirty || this.isSuggestionFeedbackFormDirty) {
      return window.confirm(  // eslint-disable-line no-alert
        gettext(
          'You have unsaved changes in this string. Navigating away will discard those changes.'
        )
      );
    }

    return true;
  },


  /*
   * Text utils
   */

  /* Highlights search results */
  hlSearch() {
    const { searchText, searchFields, searchOptions } = search.state;
    const selMap = {
      notes: 'div.developer-comments',
      locations: 'div.translate-locations',
      source: 'td.translate-original, .original .js-translation-text',
      target: 'td.translate-translation',
    };

    // Build highlighting selector based on chosen search fields
    const sel = searchFields.map((fieldName) => [
      `tr.edit-row ${selMap[fieldName]}`,
      `tr.view-row ${selMap[fieldName]}`,
    ]).reduce((a, b) => a.concat(b), []);

    let hlRegex;
    if (searchOptions.indexOf('exact') >= 0) {
      hlRegex = new RegExp(`(${escapeUnsafeRegexSymbols(searchText)})`);
    } else {
      hlRegex = new RegExp(makeRegexForMultipleWords(searchText), 'i');
    }
    $(sel.join(', ')).highlightRegex(hlRegex);
  },


  /* Copies text into the focused textarea */
  copyText(e) {
    const $el = $(e.currentTarget);
    const action = $el.data('action');
    const text = (
      $el.data('codepoint') && JSON.parse(`"${$el.data('codepoint')}"`) ||
      $el.data('string') ||
      $el.data('translation-aid') ||
      $el.text()
    );

    if (action === 'overwrite') {
      ReactEditor.setValueFor(this.focused || 0, text);
    } else {
      ReactEditor.insertAtCaretFor(this.focused || 0, text);
    }
  },

  copyTMText(e) {
    // Don't do anything if we're selecting text
    if (window.getSelection().toString() !== '') {
      return;
    }
    this.copyText(e);
  },


  /* Copies source text(s) into the target textarea(s)*/
  copyOriginal(languageCode) {
    const sources = this.units.unit.sources[languageCode];
    for (let i = 0; i < sources.length; i++) {
      ReactEditor.setValueFor(i, sources[i]);
    }

    this.goFuzzy();
  },

  copyComment(text) {
    const comment = q('.js-editor-comment');
    const commentForm = q('.js-editor-comment-form');
    const commentInput = q('#id_translator_comment');

    if (!comment.classList.contains('selected')) {
      commentForm.style.display = 'inline-block';
      comment.classList.add('selected');
    }

    commentInput.focus();
    commentInput.value = text;
  },

  /*
   * Fuzzying / unfuzzying functions
   */

  /* Sets the current unit's styling as fuzzy */
  doFuzzyStyle() {
    $('tr.edit-row').addClass('fuzzy-unit');
  },


  /* Unsets the current unit's styling as fuzzy */
  undoFuzzyStyle() {
    $('tr.edit-row').removeClass('fuzzy-unit');
  },


  /* Checks the current unit's fuzzy checkbox */
  doFuzzyBox() {
    const $checkbox = $('input.fuzzycheck');
    $checkbox.prop('checked', true);

    if (!this.settings.isAdmin) {
      if (!this.isSuggestMode()) {
        $('.js-fuzzy-block').show();
      }
      $checkbox[0].defaultChecked = true;
    }

    $checkbox.trigger('change');
  },


  /* Unchecks the current unit's fuzzy checkbox */
  undoFuzzyBox() {
    const $checkbox = $('input.fuzzycheck');
    $checkbox.prop('checked', false);
    $checkbox.trigger('change');
  },


  /* Sets the current unit status as fuzzy (both styling and checkbox) */
  goFuzzy() {
    if (!this.isFuzzy()) {
      this.doFuzzyStyle();
      this.doFuzzyBox();
    }
  },


  /* Unsets the current unit status as fuzzy (both styling and checkbox) */
  ungoFuzzy() {
    if (this.isFuzzy()) {
      this.undoFuzzyStyle();
      this.undoFuzzyBox();
    }
  },


  /* Returns whether the current unit is fuzzy or not */
  isFuzzy() {
    return $('input.fuzzycheck').prop('checked');
  },

  toggleFuzzyStyle() {
    if (this.isFuzzy()) {
      this.doFuzzyStyle();
    } else {
      this.undoFuzzyStyle();
    }
  },

  toggleState() {
    // `blur()` prevents a double-click effect if the checkbox was
    // previously clicked using the mouse
    $('input.fuzzycheck:visible').blur().click();
  },

  /* Updates unit textarea and input's `default*` values. */
  updateUnitDefaultProperties() {
    ReactEditor.setProps({ initialValues: ReactEditor.stateValues.slice() });

    const checkbox = q('#id_state');
    checkbox.defaultChecked = checkbox.checked;
    this.handleTranslationChange();
  },

  /* Updates comment area's `defaultValue` value. */
  updateCommentDefaultProperties() {
    const comment = q('#id_translator_comment');
    comment.defaultValue = comment.value;
    this.handleTranslationChange();
  },

  handleTranslationChange() {
    const comment = q('#id_translator_comment');
    const commentChanged = comment !== null ?
                           comment.value !== comment.defaultValue : false;

    const submit = q('.js-submit');
    const suggest = q('.js-suggest');
    const suggestions = $('.js-user-suggestion').map(function getSuggestions() {
      return $(this).data('translation-aid');
    }).get();
    const checkbox = q('#id_state');
    const stateChanged = checkbox.defaultChecked !== checkbox.checked;

    let needsReview = false;
    let suggestionExists = false;

    // Non-admin users are required to clear the fuzzy checkbox
    if (!this.settings.isAdmin) {
      needsReview = checkbox.checked === true;
    }

    const areaChanged = this.isTextareaValueDirty();

    const valueState = ReactEditor.stateValues;
    if (suggestions.length) {
      for (let i = 0; i < valueState.length && !suggestionExists; i++) {
        suggestionExists = suggestions.indexOf(valueState[i]) !== -1;
      }
    }

    // Store dirty state for the current unit
    this.isUnitDirty = areaChanged || stateChanged || commentChanged;

    if (submit !== null) {
      submit.disabled = !(stateChanged || areaChanged) || needsReview;
    }
    if (suggest !== null) {
      suggest.disabled = !areaChanged || suggestionExists;
    }
  },

  onStateChange() {
    this.handleTranslationChange();

    this.toggleFuzzyStyle();
  },

  onStateClick() {
    // Prevent automatic unfuzzying on explicit user action
    this.keepState = true;
  },

  onTextareaChange() {
    this.handleTranslationChange();

    if (this.isTextareaValueDirty() && !this.keepState) {
      this.ungoFuzzy();
    }

    clearTimeout(this.similarityTimer);
    this.similarityTimer = setTimeout(() => {
      this.checkSimilarTranslations();
      this.similarityTimer = null;  // So we know the code was run
    }, 200);
  },

  isTextareaValueDirty() {
    return !_.isEqual(ReactEditor.props.initialValues,
                      ReactEditor.stateValues);
  },


  /*
   * Translation's similarity
   */

  getSimilarityData() {
    const currentUnit = this.units.unit;
    return {
      similarity: currentUnit.similarityHuman,
      mt_similarity: currentUnit.similarityMT,
    };
  },

  calculateSimilarity(newTranslation, $elements, dataSelector) {
    let maxSimilarity = 0;
    let boxId = null;

    for (let i = 0; i < $elements.length; i++) {
      const $element = $elements.eq(i);
      const aidText = $element.data(dataSelector);
      const similarity = this.wordComparer.similarity(newTranslation, aidText);

      if (similarity > maxSimilarity) {
        maxSimilarity = similarity;
        boxId = $element.hasClass('js-translation-area') ?
                null : $element.val('id');
      }
    }

    return {
      boxId,
      max: maxSimilarity,
    };
  },

  checkSimilarTranslations() {
    const dataSelector = 'translation-aid';
    const dataSelectorMT = 'translation-aid-mt';
    const $aidElementsMT = $(`[data-${dataSelectorMT}]`);

    let aidElementsSelector = `[data-${dataSelector}]`;

    // Exclude own suggestions for non-anonymous users
    if (!this.settings.isAnonymous) {
      aidElementsSelector += `[data-suggestor-id!=${this.settings.userId}]`;
    }

    const $aidElements = $(aidElementsSelector);

    if (!$aidElements.length && !$aidElementsMT.length) {
      return false;
    }

    const newTranslation = ReactEditor.stateValues[0];
    let simHuman = { max: 0, boxId: null };
    let simMT = { max: 0, boxId: null };

    if ($aidElements.length) {
      simHuman = this.calculateSimilarity(newTranslation, $aidElements,
                                          dataSelector);
    }
    if ($aidElementsMT.length) {
      simMT = this.calculateSimilarity(newTranslation, $aidElementsMT,
                                       dataSelectorMT);
    }

    this.units.unit.similarityHuman = simHuman.max;
    this.units.unit.similarityMT = simMT.max;

    const similarity = (simHuman.max > simMT.max) ? simHuman : simMT;
    this.highlightBox(similarity.boxId, similarity.max === 1);
    return true;
  },

  /* Applies highlight classes to `boxId`. */
  highlightBox(boxId, isExact) {
    const bestMatchCls = 'best-match';
    const exactMatchCls = 'exact-match';

    $('.translate-table').find(`.${bestMatchCls}`)
                         .removeClass(`${bestMatchCls} ${exactMatchCls}`);

    if (boxId === null) {
      return false;
    }

    $(boxId).addClass(cx({
      [bestMatchCls]: true,
      [exactMatchCls]: isExact,
    }));
    return true;
  },


  /*
   * Suggest / submit mode functions
   */

  /* Changes the editor into suggest mode */
  doSuggestMode() {
    this.editorTableEl.classList.add('suggest-mode');
  },


  /* Changes the editor into submit mode */
  undoSuggestMode() {
    this.editorTableEl.classList.remove('suggest-mode');
  },


  /* Returns true if the editor is in suggest mode */
  isSuggestMode() {
    return this.editorTableEl.classList.contains('suggest-mode');
  },


  /* Toggles suggest/submit modes */
  toggleSuggestMode(e) {
    e.preventDefault();
    if (this.isSuggestMode()) {
      this.undoSuggestMode();
    } else {
      this.doSuggestMode();
    }
  },

  updateExportLink() {
    const $exportOpt = $('.js-export-view');
    const baseUrl = $exportOpt.data('export-url');
    const hash = utils.getHash().replace(/&?unit=\d+/, '');
    const exportLink = hash ? `${baseUrl}?${hash}` : baseUrl;

    $exportOpt.data('href', exportLink);
  },

  /*
   * Indicators, messages, error handling
   */

  showActivity() {
    this.$editorActivity.spin().fadeIn(300);
  },

  hideActivity() {
    this.$editorActivity.spin(false).fadeOut(300);
  },

  /* Displays error messages on top of the toolbar */
  displayError(text) {
    this.hideActivity();
    msg.show({ text, level: 'error' });
  },


  /* Handles XHR errors */
  error(xhr, s) {
    let text = '';

    if (s === 'abort') {
      return;
    }

    if (xhr.status === 0) {
      text = gettext('Error while connecting to the server');
    } else if (xhr.status === 402) {
      captcha.onError(xhr, 'PTL.editor.error');
    } else if (xhr.status === 404) {
      text = gettext('Not found');
    } else if (xhr.status === 500) {
      text = gettext('Server error');
    } else if (s === 'timeout') {
      text = gettext('The server seems down. Try again later.');
    } else {
      text = $.parseJSON(xhr.responseText).msg;
    }

    PTL.editor.displayError(text);
  },

  lockEditor(message) {
    const editorBody = q('.translate-full');
    editorBody.classList.add('unit-locked');

    $('.js-unit-locked-message')[0].innerText = message;
    $('.editor-area-wrapper').addClass('is-disabled');
    $('.js-translation-area').attr('disabled', 'disabled');
  },

  displayObsoleteMsg() {
    this.lockEditor(gettext('This string no longer exists.'));
  },

  /*
   * Misc functions
   */

  /* Gets common request data */
  getReqData() {
    const reqData = {};

    if (this.filter === 'checks' && this.checks.length) {
      reqData.checks = this.checks.join(',');
    }
    if (this.filter === 'checks' && this.category) {
      reqData.category = this.category;
    }


    if (this.filter === 'search') {
      const { searchText, searchFields, searchOptions } = search.state;
      reqData.search = searchText;
      reqData.sfields = searchFields;
      reqData.soptions = searchOptions;
    } else {
      reqData.filter = this.filter;
      if (this.sortBy !== 'default') {
        reqData.sort = this.sortBy;
      }
    }

    if (this.modifiedSince !== null) {
      reqData['modified-since'] = this.modifiedSince;
    }

    if (this.month !== null) {
      reqData.month = this.month;
    }

    if (this.user) {
      reqData.user = this.user;
    }

    return reqData;
  },

  getValueStateData() {
    const data = {};
    const valueState = ReactEditor.stateValues;
    for (let i = 0; i < valueState.length; i++) {
      data[getAreaId(i)] = valueState[i];
    }
    return data;
  },

  getCheckedStateData() {
    const checkbox = document.querySelector('#id_state');
    if (!checkbox.checked) {
      return {};
    }
    return {
      [checkbox.name]: checkbox.value,
    };
  },


  /*
   * Unit navigation, display, submission
   */


  /* Renders a single row */
  renderViewRow(uid, unit, extraClassName) {
    if (!unit) {
      return '';
    }

    const classNames = ['view-row'];
    if (extraClassName) {
      classNames.push(extraClassName);
    }

    return (`
      <tr id="row${uid}" class="${classNames.join(' ')}">
        ${this.tmpl.vUnit({ uid, unit })}
      </tr>
    `);
  },

  renderEditorRow(uid, unit) {
    const eClass = cx('edit-row', {
      'fuzzy-unit': unit.isfuzzy,
    });

    return (`
      <tr id="row${uid}" class="${eClass}">
        ${this.units.unit.editor}
      </tr>
    `);
  },


  /* Renders the view rows */
  renderViewRows(uids, rows) {
    for (let i = 0; i < uids.length; i++) {
      const uid = uids[i];
      const unit = this.units.units[uid];
      rows.push(this.renderViewRow(uid, unit));
    }
  },


  /* Renders the context rows */
  renderContextRows(units, rows) {
    for (let i = 0; i < units.length; i++) {
      const unit = units[i];
      const uid = unit.id;
      rows.push(this.renderViewRow(uid, unit, 'ctx'));
    }
  },


  handlePermalinkMouseover() {
    if (this.filter === 'all') {
      return;
    }
    clearTimeout(this.contextTimer);
    this.contextTimer = setTimeout(() => {
      this.units.loadContextRows();
    }, SHOW_CONTEXT_ROWS_TIMEOUT);
  },


  handlePermalinkMouseout(e) {
    if (this.filter === 'all') {
      return;
    }
    if (!e.ctrlKey) {
      this.hideContextRows();
    }
  },


  /* shows the context rows in place of regular view rows */
  showContextRows() {
    console.log('showContextRows()');

    const ctx = this.units.unit.contextData;
    if (!ctx) {
      console.warn('showContextRows() called, but this.unit.contextData is not defined');
      return;
    }

    const rowsBefore = [];
    this.renderContextRows(ctx.before, rowsBefore);

    const rowsAfter = [];
    this.renderContextRows(ctx.after, rowsAfter);

    // update DOM

    this.$contextRowsBefore.html(rowsBefore.join(''));
    this.$contextRowsAfter.html(rowsAfter.join(''));

    // hide view rows and show context rows

    this.$viewRowsBefore.addClass('context-mode');
    this.$contextRowsBefore.addClass('context-mode');

    this.$viewRowsAfter.addClass('context-mode');
    this.$contextRowsAfter.addClass('context-mode');
  },


  /* hides the context rows */
  hideContextRows() {
    console.log('hideContextRows()');
    clearTimeout(this.contextTimer);

    if (!this.$contextRowsBefore.hasClass('context-mode')) {
      return; // nothing to do
    }

    // hide context rows and show view rows

    this.$viewRowsBefore.removeClass('context-mode');
    this.$contextRowsBefore.removeClass('context-mode');

    this.$viewRowsAfter.removeClass('context-mode');
    this.$contextRowsAfter.removeClass('context-mode');
  },

  /* populates lead-in and lead-out row messages */
  populateLeadInOutMessages() {
    const leadIn = [];
    const leadOut = [];

    const canShow = this.units.ready && (this.units.uids.length >
      this.units.visibleRowsBefore + this.units.visibleRowsAfter);

    if (canShow) {
      if (this.units.begin === 0) {
        leadIn.push(nt(
          'Found %(total)s unit.',
          'Found %(total)s units.',
          this.units.total, { total: this.units.total }));
      } else {
        // there are some units above;
        // this can only happen when filter is set to 'all'
        leadIn.push(nt(
          'There are %(count)s more unit above.',
          'There are %(count)s more units above.',
          this.units.total, { count: this.units.begin }));

        leadIn.push(t('Reload the page to see them.'));
      }

      if (this.units.end === this.units.total) {
        leadOut.push(t('Congratulations, you went through all units!'));
      } else {
        leadOut.push(t('Congratulations, you went through a good number of units!'));

        if (this.filter === 'all') {
          leadOut.push(t(
            'Reload the page to see some more.'));
        } else if (this.filter === 'search') {
          leadOut.push(t(
            `There were more units that matched your search criteria.
            Please refine your search.`));
        } else {
          leadOut.push(t(
            `There were more units that matched your filter.
            Reload the page to see if there's more stuff to go through,
            or use search to find specific units.`));
        }
      }
    }

    return { leadIn, leadOut };
  },

  /* redraws the translate table view rows */
  redrawViewRows() {
    console.log('redrawViewRows()');

    const messages = this.populateLeadInOutMessages();

    const rowsBefore = [];
    rowsBefore.push(`
      <tr>
        <td colspan="2" class="lead-in-row"><p>${messages.leadIn.join('</p><p>')}</p></td>
      </tr>
    `);
    this.renderViewRows(this.units.visibleUnitsBefore(), rowsBefore);

    const rowsAfter = [];
    this.renderViewRows(this.units.visibleUnitsAfter(), rowsAfter);
    rowsAfter.push(`
      <tr>
        <td colspan="2" class="lead-out-row"><p>${messages.leadOut.join('</p><p>')}</p></td>
      </tr>
    `);

    // update DOM

    this.$viewRowsBefore.html(rowsBefore.join(''));
    this.$viewRowsAfter.html(rowsAfter.join(''));
  },


  /* redraws the edit row */
  redrawEditRow() {
    let editorRow = '';
    if (this.editorIsClosed) {
      /* when the editor is closed, it is rendered as a view row but in the context
       of the editor row section; we need to adjust its background so that it follows
       the background stripe pattern of the upper view rows */
      const rowsBefore = this.units.visibleUnitsBefore().length + 1; // add 1 for lead-in-row
      const className = rowsBefore % 2 === 1 ? 'even' : undefined;

      editorRow = this.renderViewRow(this.units.uid, this.units.unit, className);
    } else {
      editorRow = this.renderEditorRow(this.units.uid, this.units.unit);
    }

    this.$editorRow.html(editorRow);
    this.ready();
  },


  /* redraws all translate table rows */
  redrawRows() {
    this.redrawViewRows();
    this.redrawEditRow();
  },

  /* Updates a button in `selector` to the `enable` state */
  updateNavButton($button, enable) {
    // Avoid unnecessary actions
    if ($button.is(':enabled') && enable || $button.is(':disabled') && !enable) {
      return;
    }

    if (enable) {
      $button.attr('title', $button.data('title'));
    } else {
      $button.data('title', $button.attr('title'));
      $button.removeAttr('title');
    }
    $button.prop('disabled', !enable);
  },


  /* Updates the navigation widget */
  updateNavigation() {
    this.updateNavButton(this.$navPrev,
                         !this.units.onFirstUnit());
    this.updateNavButton(this.$navNext, !this.units.onLastUnit());

    this.unitPositionEl.innerText = this.units.getPosition();
    this.unitCountEl.innerText = this.units.total;
  },


  /* Update edit row, because currently selected unit has changed */
  handleUnitChange(uid) {
    console.log('handleUnitChange(), uid:', uid);
    this.editorIsClosed = false;
    // When we're going to the first unit (and change the URL as a consequence),
    // we want to treat this as an 'internal redirect' and not to push it
    // into history stack
    const hashUid = parseInt(utils.getParsedHash().unit, 10);

    if (!hashUid) {
      console.log('history.replaceState()');
      history.replaceState(undefined, undefined, `#${utils.updateHashPart('unit', uid)}`);
    } else {
      if (uid !== hashUid) {
        console.log('history.pushState()');
        history.pushState(undefined, undefined, `#${utils.updateHashPart('unit', uid)}`);
      }
    }
    this.updateNavigation();
    this.hideContextRows();
    this.redrawRows(); // redraw both unit and view rows
  },


  /* Handle the 'No units found' case */
  handleEmptyResults() {
    this.editorIsClosed = true;
    this.isLoading = false;
    this.hideActivity();
    this.updateNavigation();
    this.hideContextRows();

    this.$viewRowsBefore.html(`
      <tr>
        <td colspan="2" class="no-results-row"><p>${t('No units found.')}</p></td>
      </tr>
    `);
    this.$editorRow.html('');
    this.$viewRowsAfter.html('');
  },


  /* Update view rows, because they have changed */
  handleViewRowsChange(uid) {
    console.log('handleViewRowsChange(), uid:', uid);
    this.redrawViewRows();
  },


  /* Pushes translation submissions and moves to the next unit */
  handleSubmit(comment = '') {
    const el = q('input.submit');
    const newTranslation = ReactEditor.stateValues[0];
    const suggestions = $('.js-user-suggestion').map(function getSuggestions() {
      return {
        text: this.dataset.translationAid,
        id: this.dataset.suggId,
      };
    }).get();
    const captchaCallbacks = {
      sfn: 'PTL.editor.processSubmission',
      efn: 'PTL.editor.error',
    };

    this.updateUnitDefaultProperties();

    // Check if the string being submitted is already in the set of
    // suggestions
    // FIXME: this is LAME, I wanna die: we need to use proper models!!
    const suggestionIds = _.pluck(suggestions, 'id');
    const suggestionTexts = _.pluck(suggestions, 'text');
    const suggestionIndex = suggestionTexts.indexOf(newTranslation);

    if (suggestionIndex !== -1 && !this.isFuzzy()) {
      if (this.settings.canReview) {
        this.acceptSuggestion(suggestionIds[suggestionIndex], { skipToNext: true });
        return;
      }
      // Exact match suggestions are still accepted this way for users
      // with no review right
      this.selectedSuggestionId = suggestionIds[suggestionIndex];
    }

    // If similarities were in the process of being calculated by the time
    // the submit button was clicked, clear the timer and calculate them
    // straight away
    if (this.similarityTimer !== null) {
      clearTimeout(this.similarityTimer);
      this.checkSimilarTranslations();
    }

    const body = assign({}, this.getCheckedStateData(), this.getValueStateData(),
                        this.getReqData(), this.getSimilarityData(),
                        captchaCallbacks);

    el.disabled = true;

    // Check if we used a suggestion
    if (this.selectedSuggestionId !== undefined) {
      const suggData = {
        suggestion: this.selectedSuggestionId,
        comment,
      };
      assign(body, suggData);
    }

    UnitAPI.addTranslation(this.units.uid, body)
      .then(
        (data) => this.processSubmission(data),
        this.error
      );
  },

  processSubmission(data) {
    if (this.selectedSuggestionId !== undefined) {
      this.processAcceptSuggestion(data, this.selectedSuggestionId);
      return;
    }

    const unit = this.units.unit;
    unit.setTranslation(ReactEditor.stateValues);
    unit.setFuzzy(this.isFuzzy());

    const hasCriticalChecks = !!data.checks;
    $('.translate-container').toggleClass('error', hasCriticalChecks);

    if (data.user_score) {
      score.set(data.user_score);
    }

    if (hasCriticalChecks) {
      _refreshChecksSnippet(data.checks);
    } else {
      this.gotoNext();
    }
  },

  /* Pushes translation suggestions and moves to the next unit */
  handleSuggest() {
    const captchaCallbacks = {
      sfn: 'PTL.editor.processSuggestion',
      efn: 'PTL.editor.error',
    };

    this.updateUnitDefaultProperties();

    const body = assign({}, this.getValueStateData(), this.getReqData(),
                        this.getSimilarityData(), captchaCallbacks);

    UnitAPI.addSuggestion(this.units.uid, body)
      .then(
        (data) => this.processSuggestion(data),
        this.error
      );
  },

  processSuggestion(data) {
    if (data.user_score) {
      score.set(data.user_score);
    }

    this.gotoNext();
  },


  /* Loads the previous unit */
  gotoPrev() {
    if (!this.canNavigate()) {
      return false;
    }
    this.units.gotoPrev();
    return true; // TODO: check if we are using this return value
  },


  /* Loads the next unit */
  gotoNext(opts = { isSubmission: true }) {
    if (!this.canNavigate()) {
      return false;
    }
    if (this.units.onLastUnit()) {
      if (opts.isSubmission) {
        // On submitting the last unit in a sequence, 'close' the editor row
        this.editorIsClosed = true;
        this.redrawRows();
      }
      return true; // TODO: check if we are using this return value
    }
    this.units.gotoNext();
    return true; // TODO: check if we are using this return value
  },


  /* Loads the editor with a specific unit */
  gotoUnit(e) {
    e.preventDefault();

    if (!PTL.editor.canNavigate()) {
      return false;
    }

    // Ctrl + click / Alt + click / Cmd + click / Middle click opens a new tab
    if (e.ctrlKey || e.altKey || e.metaKey || e.which === 2) {
      const $el = e.target.nodeName !== 'TD' ?
                  $(e.target).parents('td') :
                  $(e.target);
      window.open($el.data('target'), '_blank');
      return false;
    }

    // Don't load anything if we're just selecting text or right-clicking
    if (window.getSelection().toString() !== '' || e.which === 3) {
      return false;
    }

    // Get clicked unit's uid from the row's id information and
    // try to load it
    const m = this.id.match(/row([0-9]+)/);
    if (m) {
      const uid = parseInt(m[1], 10);
      if ($(this).hasClass('ctx')) {
        // reset the current filter
        $.history.load(`/unit/${encodeURIComponent(uid)}`);
      } else {
        PTL.editor.units.goto(uid);
      }
    }
    return true;
  },

  /*
   * Units filtering
   */

  /* Gets the failing check options for the current query */
  getCheckOptions() {
    console.log('getCheckOptions()');
    StatsAPI.getChecks(this.settings.pootlePath)
      .then(
        (data) => this.updateChecksDropdown(data),
        this.error
      );
  },

  /* Loads units based on checks filtering */
  filterChecks() {
    if (this.preventNavigation) {
      return false;
    }
    if (!this.canNavigate()) {
      return false;
    }

    const name = this.$filterChecks.val();
    const isCategory = $(this.$filterChecks.select2('data').element).data('type') === 'category';

    const sortBy = this.$filterSortBy.val();
    const newHash = {
      filter: 'checks',
    };

    if (name !== 'all') {
      if (isCategory) {
        newHash.category = name;
      } else {
        newHash.checks = name;
      }
    }

    if (sortBy !== 'default') {
      newHash.sort = sortBy;
    }

    $.history.load($.param(newHash));
    return true;
  },

  /* Adds the failing checks to the UI */
  updateChecksDropdown(checks) {
    const $checks = this.$filterChecks;

    $checks.find('optgroup').each(function displayGroups() {
      const $gr = $(this);
      let groupTotal = 0;

      $gr.find('option').each(function displayOptions() {
        const $opt = $(this);
        const value = $opt.val();

        if ($opt.hasClass('category')) {
          return;
        }

        if (value in checks) {
          groupTotal += checks[value];
        } else {
          $opt.remove();
        }
      });

      if (groupTotal === 0) {
        $gr.hide();
      }
    });
  },

  filterSort() {
    const filterBy = this.$filterStatus.val();
    // #104: Since multiple values can't be selected in the select
    // element, we also need to check for `this.checks`.
    const filterChecks = this.$filterChecks.val() || this.checks.join(',');
    const sortBy = this.$filterSortBy.val();
    const user = this.user || null;

    const newHash = {};
    if (filterBy !== 'all') {
      newHash.filter = filterBy;
    }

    if (this.category) {
      newHash.category = this.category;
    } else if (filterChecks !== 'none') {
      newHash.checks = filterChecks;
    }

    if (sortBy !== 'default') {
      newHash.sort = sortBy;
    }
    if (user !== null) {
      newHash.user = user;
    }

    $.history.load($.param(newHash));
  },


  /* Loads units based on filtering */
  filterStatus() {
    if (!this.canNavigate()) {
      return false;
    }

    // this function can be executed in different contexts,
    // so using the full selector here
    const $selected = this.$filterStatus.find('option:selected');
    const filterBy = $selected.val();

    this.$filterChecksWrapper.hide();

    if (!this.preventNavigation) {
      const newHash = {};
      if (filterBy !== 'all') {
        newHash.filter = filterBy;
      }
      const isUserFilter = $selected.data('user');

      if (this.user && isUserFilter) {
        newHash.user = this.user;
      } else {
        this.user = null;
        $('.js-user-filter').remove();

        if (this.sortBy !== 'default') {
          newHash.sort = this.sortBy;
        }
      }

      $.history.load($.param(newHash));
    }
    return true;
  },


  /* Loads the search view */
  onSearch(searchText) {
    if (!PTL.editor.canNavigate()) {
      return false;
    }

    let newHash;

    if (searchText) {
      const queryString = this.buildSearchQuery();
      newHash = `search=${queryString}`;
    } else {
      newHash = utils.updateHashPart(undefined, undefined,
        ['filter', 'search', 'sfields', 'soptions']);
    }
    $.history.load(newHash);
    return true;
  },


  /*
   * Comments
   */

  addComment(e) {
    e.preventDefault();
    this.updateCommentDefaultProperties();

    UnitAPI.addComment(this.units.uid, $(e.target).serializeObject())
      .then(
        (data) => this.processAddComment(data),
        this.error
      );
  },

  processAddComment(data) {
    $('.js-editor-comment').removeClass('selected');
    $('#editor-comment').fadeOut(200);

    if ($('#translator-comment').length) {
      $(data.comment).hide().prependTo('#translator-comment').delay(200)
        .animate({ height: 'show' }, 1000, 'easeOutQuad');
    } else {
      $(`<div id='translator-comment'>${data.comment}</div>`)
        .prependTo('#extras-container').delay(200)
        .hide().animate({ height: 'show' }, 1000, 'easeOutQuad');
    }

    helpers.updateRelativeDates();
  },

  /* Removes last comment */
  removeComment(e) {
    e.preventDefault();

    UnitAPI.removeComment(this.units.uid)
      .then(
        () => $('.js-comment-first').fadeOut(200),
        this.error
      );
  },


  /*
   * Unit timeline
   */

  /* Get the timeline data */
  showTimeline() {
    const $results = $('#timeline-results');
    if ($results.length) {
      $results.slideDown(1000, 'easeOutQuad');
      return;
    }

    const $node = $('.translate-container');
    $node.spin();

    UnitAPI.getTimeline(this.units.uid)
      .then(
        (data) => this.renderTimeline(data),
        this.error
      )
      .always(() => $node.spin(false));
  },

  renderTimeline(data) {
    const uid = data.uid;

    if (data.timeline && uid === this.units.uid) {
      if ($('#translator-comment').length) {
        $(data.timeline).hide().insertAfter('#translator-comment')
                        .slideDown(1000, 'easeOutQuad');
      } else {
        $(data.timeline).hide().prependTo('#extras-container')
                        .slideDown(1000, 'easeOutQuad');
      }
      qAll('.js-mount-timesince').forEach((el, i) => {
        const props = {
          title: data.entries_group[i].display_datetime,
          dateTime: data.entries_group[i].iso_datetime,
        };
        if (data.entries_group[i].via_upload) {
          ReactRenderer.render(<UploadTimeSince {...props} />, el);
        } else {
          ReactRenderer.render(<TimeSince {...props} />, el);
        }
      });

      utils.highlightRONodes('.js-unit-highlight');

      $('.timeline-field-body').filter(':not([dir])').bidi();
      $('#js-show-timeline').addClass('selected');
    }
  },

  /* Hide the timeline panel */
  toggleTimeline(e) {
    e.preventDefault();
    const $timelineToggle = $('#js-toggle-timeline');
    $timelineToggle.toggleClass('selected');
    if ($timelineToggle.hasClass('selected')) {
      this.showTimeline();
    } else {
      $('#timeline-results').slideUp(1000, 'easeOutQuad');
    }
  },


  /*
   * User and TM suggestions
   */

  /* Filters TM results and does some processing */
  filterTMResults(results, sourceText) {
    // FIXME: this just retrieves the first three results
    // we could limit based on a threshold too.
    const filtered = [];

    // FIXME: move this side-effect elsewhere
    if (results.length > 0 && results[0].source === sourceText) {
      if (ReactEditor.stateValues[0] === '') {
        // save unit editor state to restore it after autofill changes
        const isUnitDirty = this.isUnitDirty;
        const text = results[0].target;
        ReactEditor.setValueFor(this.focused || 0, text);
        this.goFuzzy();
        this.isUnitDirty = isUnitDirty;
      }
    }

    for (let i = 0; i < results.length && i < 3; i++) {
      const result = results[i];
      let fullname = result.fullname;
      if (result.username === 'nobody') {
        fullname = gettext('some anonymous user');
      } else if (!result.fullname) {
        fullname = result.username ? result.username : gettext('someone');
      }
      result.fullname = _.escape(fullname);
      result.project = _.escape(result.project);
      result.path = _.escape(result.path);

      filtered.push(result);
    }

    return filtered;
  },

  /* TM suggestions */
  getTMUnitsContent(data) {
    const unit = this.units.unit;
    if (!unit) {
      console.error('getTMUnitsContent(), unit is not defined');
      return '';
    }
    const store = ''; // was: unit.get('store'); TODO: why do we need store for TM?
    const sourceText = unit.sourceText();
    const filtered = this.filterTMResults(data, sourceText);
    const name = gettext('Similar translations');

    if (filtered.length) {
      return this.tmpl.tm({
        name,
        store: store.toJSON(),
        unit: sourceText, // was: unit.toJSON(), TODO: review
        suggs: filtered,
      });
    }

    return '';
  },

  /* Gets TM suggestions from amaGama */
  getTMUnits() {
    const unit = this.units.unit;
    const store = ''; // was: unit.get('store'); TODO: why do we need store for TM?
    const src = unit.srcLang;
    const tgt = unit.targetLang;
    const sText = unit.sourceText();

    if (!sText.length || src === tgt) {
      return;
    }

    const pStyle = store.get('project_style');
    let tmUrl = `${this.settings.tmUrl}${src}/${tgt}/unit/` +
      `?source=${encodeURIComponent(sText)}`;

    if (pStyle.length && pStyle !== 'standard') {
      tmUrl += `&style=${pStyle}`;
    }

    fetch({ url: tmUrl, crossDomain: true })
      .then(
        (data) => this.handleTmResults(data, store, unit),
        // eslint-disable-next-line no-console
        (xhr, s) => console.error(`HTTP ${xhr.status} (${s}): ${tmUrl}`)
      );
  },

  handleTmResults(data, store, unit) {
    if (!data.length) {
      return false;
    }

    const sourceText = unit.get('source')[0];
    const filtered = PTL.editor.filterTMResults(data, sourceText);
    const name = gettext('Similar translations');
    const tm = PTL.editor.tmpl.tm({
      name,
      store: store.toJSON(),
      unit: unit.toJSON(),
      suggs: filtered,
    });

    $(tm).hide().appendTo('#extras-container')
                .slideDown(1000, 'easeOutQuad');
    return true;
  },


  /* Rejects a suggestion */
  handleRejectSuggestion(suggId, { requestData = {} } = {}) {
    this.rejectSuggestion(suggId, { requestData });
  },

  rejectSuggestion(suggId, { requestData = {} } = {}) {
    UnitAPI.rejectSuggestion(this.units.uid, suggId, requestData)
      .then(
        (data) => this.processRejectSuggestion(data, suggId),
        this.error
      );
  },

  processRejectSuggestion(data, suggId) {
    if (data.user_score) {
      score.set(data.user_score);
    }

    $(`#suggestion-${suggId}`).fadeOut(200, function handleRemove() {
      PTL.editor.closeSuggestion({ checkIfCanNavigate: false });
      $(this).remove();

      // Go to the next unit if there are no more suggestions left
      if (!$('.js-user-suggestion').length) {
        PTL.editor.gotoNext();
      }
    });
  },


  /* Accepts a suggestion */
  handleAcceptSuggestion(
    suggId, { requestData = {}, isSuggestionChanged = false } = {}
  ) {
    if (isSuggestionChanged) {
      const area = q('.js-translation-area');
      area.value = decodeEntities(requestData.translation);
      this.undoFuzzyBox();
      this.handleSubmit(requestData.comment);
    } else {
      this.acceptSuggestion(suggId, { requestData });
    }
  },

  acceptSuggestion(suggId, { requestData = {}, skipToNext = false } = {}) {
    UnitAPI.acceptSuggestion(this.units.uid, suggId, requestData)
    .then(
      (data) => this.processAcceptSuggestion(data, suggId, skipToNext),
      this.error
    );
  },

  processAcceptSuggestion(data, suggId, skipToNext) {
    if (data.newtargets !== undefined) {
      for (let i = 0; i < data.newtargets.length; i++) {
        ReactEditor.setValueFor(i, data.newtargets[i]);
      }
    }
    this.updateUnitDefaultProperties();

    const unit = this.units.unit;
    unit.setTranslation(ReactEditor.stateValues);
    unit.setFuzzy(false);

    highlightSuggestionsDiff(unit);

    if (data.user_score) {
      score.set(data.user_score);
    }

    const hasCriticalChecks = !!data.checks;
    $('.translate-container').toggleClass('error', hasCriticalChecks);
    if (hasCriticalChecks) {
      _refreshChecksSnippet(data.checks);
    }

    $(`#suggestion-${suggId}`).fadeOut(200, function handleRemove() {
      PTL.editor.closeSuggestion({ checkIfCanNavigate: false });
      $(this).remove();

      // Go to the next unit if there are no more suggestions left,
      // provided there are no critical failing checks
      if (!hasCriticalChecks && (skipToNext || !$('.js-user-suggestion').length)) {
        PTL.editor.gotoNext();
      }
    });
  },

  /* Mutes or unmutes a quality check marking it as false positive or not */
  toggleCheck(checkId) {
    const $check = $(`.js-check-${checkId}`);
    const isFalsePositive = $check.hasClass('false-positive');

    const opts = isFalsePositive ? null : { mute: 1 };
    UnitAPI.toggleCheck(this.units.uid, checkId, opts)
      .then(
        () => this.processToggleCheck(checkId, isFalsePositive),
        this.error
      );
  },

  processToggleCheck(checkId, isFalsePositive) {
    $(`.js-check-${checkId}`).toggleClass('false-positive', !isFalsePositive);

    const hasError = $('#translate-checks-block .check')
      .not('.false-positive').size() > 0;

    $('.translate-container').toggleClass('error', hasError);
  },

  /*
   * Machine Translation
   */

  runHooks() {
    mtProviders.forEach((provider) => provider.init({
      unit: assign(this.units.unit),
    }));
  },

  /* FIXME: provide an alternative to such an ad-hoc entry point */
  setTranslation(opts) {
    const { translation } = opts;
    if (translation === undefined && opts.msg) {
      this.displayError(opts.msg);
      return false;
    }

    ReactEditor.setValueFor(this.focused || 0, decodeEntities(translation));

    // Save a copy of the resulting text in the DOM for further
    // similarity comparisons
    this.focused.dataset.translationAidMt = translation;

    this.goFuzzy();

    return true;
  },

  openSuggestion(suggId, initialSuggestionText) {
    const suggestion = document.getElementById(`suggestion-${suggId}`);

    this.selectedSuggestionId = suggId;
    const props = {
      suggId,
      initialSuggestionText,
      localeDir: this.settings.localeDir,
      onAcceptSuggestion: this.handleAcceptSuggestion.bind(this),
      onRejectSuggestion: this.handleRejectSuggestion.bind(this),
      onChange: this.handleSuggestionFeedbackChange.bind(this),
    };
    const mountSelector = `.js-mnt-suggestion-feedback-${suggId}`;
    const feedbackMountPoint = q(mountSelector);
    const editorBody = q('.translate-full');
    suggestion.classList.add('suggestion-expanded');
    editorBody.classList.add('suggestion-expanded');

    this.isSuggestionFeedbackFormDirty = false;
    ReactDOM.render(
      <SuggestionFeedbackForm {...props} />,
      feedbackMountPoint
    );
  },

  toggleSuggestion(e, { canHide = false } = {}) {
    if (this.selectedSuggestionId === undefined) {
      e.stopPropagation();
      const suggestionId = parseInt(e.currentTarget.dataset.suggId, 10);
      const initialSuggestionText = e.currentTarget.dataset.translationAid;
      this.openSuggestion(suggestionId, initialSuggestionText);
    } else if (canHide) {
      e.stopPropagation();
      this.closeSuggestion();
    }
  },

  handleSuggestionFeedbackChange(isDirty) {
    this.isSuggestionFeedbackFormDirty = isDirty;
  },

  closeSuggestion({ checkIfCanNavigate = true } = {}) {
    if (this.selectedSuggestionId !== undefined &&
        (!checkIfCanNavigate || this.canNavigate())) {
      const suggestion = q(`#suggestion-${this.selectedSuggestionId}`);
      const editorBody = q('.translate-full');
      const mountSelector = `.js-mnt-suggestion-feedback-${this.selectedSuggestionId}`;
      const feedbackMountPoint = q(mountSelector);
      editorBody.classList.remove('suggestion-expanded');
      suggestion.classList.remove('suggestion-expanded');
      ReactDOM.unmountComponentAtNode(feedbackMountPoint);
      this.selectedSuggestionId = undefined;
      this.isSuggestionFeedbackFormDirty = false;
    }
  },
};
