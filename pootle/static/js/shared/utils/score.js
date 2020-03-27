/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import { t } from './i18n';

export function getScoreText(score) {
  if (score > 0) {
    return t('+%(score)s', { score });
  }
  return score;
}
