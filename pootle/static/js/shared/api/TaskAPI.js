/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import fetch from 'utils/fetch';


const TaskAPI = {

  apiRoot: '/xhr/tasks/',

  get(languageCode, { offset = 0, limit = 0 } = {}) {
    let url = `${this.apiRoot}${languageCode}/`;
    const params = {};

    if (offset > 0) {
      params.offset = offset;
    }
    if (limit > 0) {
      params.limit = limit;
    }

    const qs = Object.keys(params).map(
      key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`
    ).join('&');
    if (qs) {
      url = `${url}?${qs}`;
    }

    return fetch({ url });
  },

};


export default TaskAPI;
