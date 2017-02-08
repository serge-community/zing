/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import assign from 'object-assign';

import fetch from 'utils/fetch';


const jsonFetch = (opts) => fetch(assign({}, opts, {
  contentType: 'application/json',
  body: JSON.stringify(opts.body),
}));


const DueDateAPI = {

  apiRoot: '/xhr/duedates/',

  add(path, isoDate) {
    const body = {
      due_on: isoDate,
      pootle_path: path,
    };
    return jsonFetch({
      body,
      method: 'POST',
      url: this.apiRoot,
    });
  },

  update(id, isoDate) {
    const body = {
      due_on: isoDate,
    };
    return jsonFetch({
      body,
      method: 'PUT',
      url: `${this.apiRoot}${id}/`,
    });
  },

  remove(id) {
    return jsonFetch({
      method: 'DELETE',
      url: `${this.apiRoot}${id}/`,
    });
  },

};


export default DueDateAPI;
