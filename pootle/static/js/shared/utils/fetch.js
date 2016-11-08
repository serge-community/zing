/*
 * Copyright (C) Pootle contributors.
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import $ from 'jquery';


const requests = {};


function fetch({ url, body, method = 'GET', dataType = 'json', queue = null,
                 crossDomain = false }) {
  const queueName = queue || url;

  if (requests[queueName]) {
    requests[queueName].abort();
  }

  const timeId = `fetch: ${method} ${url}`;
  console.time(timeId);
  console.log('fetch request data:', body);
  requests[queueName] = (
    $.ajax({
      crossDomain,
      method,
      dataType,
      url: l(url),
      data: body,
    })
  );
  requests[queueName].done(() => {
    console.timeEnd(timeId);
    console.log('fetched JSON:', requests[queueName].responseJSON);
    requests[queueName] = null;
  });
  return requests[queueName];
}


export default fetch;
