# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.


# Maximal number of top contributors which is loaded for each request
TOP_CONTRIBUTORS_CHUNK_SIZE = 10


def get_top_scorers_data(top_scorers, chunk_size):
    has_more_scorers = len(top_scorers) > chunk_size

    top_scorers_data = [
        dict(
            public_total_score=scorer['public_total_score'],
            suggested=scorer['suggested'],
            translated=scorer['translated'],
            reviewed=scorer['reviewed'],
            email=scorer['user'].email_hash,
            display_name=scorer['user'].display_name,
            username=scorer['user'].username,
        ) for scorer in top_scorers[:chunk_size]
    ]

    return dict(
        items=top_scorers_data,
        has_more_items=has_more_scorers
    )
