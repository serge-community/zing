/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */


class Unit {

  constructor({ id, source, sourceLang, target, targetLang }) {
    this.id = id;
    this.source = source;
    this.sourceLang = sourceLang;
    this.target = target;
    this.targetLang = targetLang;

    // TODO: get direction from language; update viewRow template not to
    // use this structure
    this.store = {
      source_lang: this.sourceLang,
      source_dir: 'ltr',
      target_lang: this.targetLang,
      target_dir: 'ltr',
    };
    this.url = l(`/unit/${this.id}`);
  }

  provideFullData(data) {
    this.sources = data.sources;
    this.source = data.sources[this.sourceLang];
    this.target = data.target;
    this.editor = data.editor;
    this.isfuzzy = data.isfuzzy;
    this.is_obsolete = data.is_obsolete;
    this.tm_suggestions = data.tm_suggestions;
  }

  sourceText() {
    return this.source ? this.source : [''];
  }

  targetText() {
    return this.target ? this.target : [''];
  }

  isFullyLoaded() {
    return !!this.editor;
  }

  // FIXME: don't do this after moving to React
  // Until we have a React editor component that properly redraws itself based
  // on Unit object data, we want to reload the editor from the server upon
  // updating unit properties
  invalidateEditor() {
    this.editor = undefined;
  }

  setFuzzy(value) {
    this.isfuzzy = value;
  }

  setTranslation(values) {
    this.target = values;
  }
}


export default Unit;
