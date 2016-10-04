/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import assign from 'object-assign';

class Unit {

  constructor(opts) {
    assign(this, opts);
    this.id = 12345; // TODO: get real value
    this.srcLang = 'en'; // TODO: get real value
    this.targetLang = 'ru'; // TODO: get real value
    // TODO: get direction from language; update viewRow template not to use this structure
    this.store = {
      source_lang: this.srcLang,
      source_dir: 'ltr',
      target_lang: this.targetLang,
      target_dir: 'ltr',
    };
    this.url = `/unit/${this.id}`;
  }

  // FIXME: support plurals
  sourceText() {
    return this.source ? this.source[0] : '';
  }

  // FIXME: support plurals
  targetText() {
    return this.target ? this.target[0] : '';
  }

  isFullyLoaded() {
    return !!this.editor;
  }

  // FIXME: don't do this after moving to React
  // Until we have a React editor component that properly
  // redraws itself based on Unit object data, we want
  // to reload the editor from the server upon updating
  // unit properties
  invalidateEditor() {
    this.editor = undefined;
  }

  setFuzzy(value) {
    this.isfuzzy = value;
    this.invalidateEditor();
  }

  setTranslation(values) {
    this.target = values;
    this.invalidateEditor();
  }
}


export default Unit;
