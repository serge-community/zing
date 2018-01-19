# -*- coding: utf-8 -*-
#
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

# To avoid rereading and reparsing translation files from disk on
# every request, Zing keeps a pool of already parsed files in memory.
#
# Larger pools will offer better performance, but higher memory usage
# (per server process). When the pool fills up, 1/PARSE_POOL_CULL_FREQUENCY
# number of files will be removed from the pool.
PARSE_POOL_SIZE = 40
PARSE_POOL_CULL_FREQUENCY = 4

# Certain items such as template fragments, permissions, language
# and project names etc are cached. These are kept in memory for the duration in
# seconds defined here.
CACHE_TIMEOUT = 604800
