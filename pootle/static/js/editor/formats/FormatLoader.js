/*
 * Copyright (C) Pootle contributors.
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import FormatAdaptor from './FormatAdaptor';


/* Detects format adaptor by options and runs onLoad callback with it */
export function loadFormatAdaptor(options, onLoad) {
  const props = Object.assign({}, options);
  delete props.fileType;

  switch (options.fileType) {
    default: {
      onLoad(props, FormatAdaptor);
    }
  }
}
