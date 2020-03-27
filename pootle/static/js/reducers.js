/*
 * Copyright (C) Pootle contributors.
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import { combineReducers } from 'redux';

import auth from './auth/reducers';

let asyncReducers = {};

export function registerReducers(newReducers) {
  asyncReducers = Object.assign({}, asyncReducers, newReducers);
}

function createReducer() {
  return combineReducers(Object.assign({}, { auth }, asyncReducers));
}

export default createReducer;
