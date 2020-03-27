/*
 * Copyright (C) Pootle contributors.
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';

import CodeMirror from 'components/CodeMirror';
import 'codemirror/mode/htmlmixed/htmlmixed';

const propTypes = {
  // Temporarily needed to support submitting forms not controlled by JS
  name: React.PropTypes.string,
  onChange: React.PropTypes.func,
  style: React.PropTypes.object,
  value: React.PropTypes.string,
};

function ContentEditor({ name, onChange, style, value }) {
  const mode = 'htmlmixed';

  return (
    <div className="content-editor" style={style}>
      <CodeMirror
        mode={mode}
        name={name}
        value={value}
        onChange={onChange}
        placeholder={gettext('Allowed markup: HTML')}
      />
    </div>
  );
}
ContentEditor.propTypes = propTypes;

export default ContentEditor;
