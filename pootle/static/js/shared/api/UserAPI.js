/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import fetch from 'utils/fetch';

function prepareData(data) {
  return JSON.stringify(data);
}

const UserAPI = {
  apiRoot: '/xhr/users/',

  update(userId, body) {
    return fetch({
      body: prepareData(body),
      method: 'PUT',
      url: `${this.apiRoot}${userId}`,
    });
  },
};

export default UserAPI;
