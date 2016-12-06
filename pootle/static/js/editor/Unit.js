/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import { dir } from 'utils/i18n';


class Unit {

  constructor({
    id, source, sourceLang, target, targetLang,
    targetLanguageName, projectName, file,
  }) {
    this.id = id;
    this.source = source;
    this.sourceDir = dir(sourceLang);
    this.sourceLang = sourceLang;
    this.target = target;
    this.targetDir = dir(targetLang);
    this.targetLang = targetLang;
    this.targetLanguageName = targetLanguageName;
    this.projectName = projectName;
    this.file = file;

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
