#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# An experimental Spotify Proposer
#
# Copyright (C) Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Authors:
#   Alvaro del Castillo San Felix <acs@bitergia.com>
#
import json
import operator
import os.path

import explorer

SPOTIFY_USER = 'acsspotify'
SCOPES = 'user-library-read,user-read-recently-played,user-top-read,user-follow-read'


def find_artists_recommendations(token, seed_artists_ids=[]):
    """
    Using recommendations API get a list of recommended artists using seed_artists as seed

    :param token: User auth token
    :param seed_artists_ids: list with artists ids to be used as seed
    :return: a list of artists
    """

    artists = []

    limit = 100
    offset = 0
    max_seed_artists = 5
    while True:
        seed = seed_artists_ids[offset:offset + max_seed_artists]
        if not seed:
            break
        # The seed must be a list with 5 artists ids
        seed = "seed_artists=" + ",".join(seed)
        recommend_url = explorer.SPOTIFY_API + "/recommendations?limit=%i&%s" % (limit, seed)
        tracks = explorer.query_api(token, recommend_url)

        # Now we need to extract the artists from the tracks
        # The artist object included is the simplified one
        for track in tracks['tracks']:
            artists.append(track['artists'][0])
        offset += max_seed_artists

    return artists


def find_related_artists(token, seed_artists_ids=[]):
    """
    Using the related API get a list of related artists to seed_artists

    :param token: User auth token
    :param seed_artists_ids: list with artists ids to be used as seed
    :return: a list of artists
    """

    artists = []

    for artist_id in seed_artists_ids:
        related_url = explorer.SPOTIFY_API + "/artists/%s/related-artists" % (artist_id)
        related_artists = explorer.query_api(token, related_url)
        artists += related_artists['artists']

    return artists


def find_artists(token):
    """
    Get new artists recommendations for the user of the token

    For finding new artists to follow we use the Spotify recommendations
    and the related artists based on the followed and top user current artists.

    :param token: User auth token
    :return: A list of artists names not known by the user
    """

    followed = explorer.find_user_followed_artists(token)
    top = explorer.find_user_tops(token, kind='artists')

    followed_names = set([a['name'] for a in followed])
    followed_ids = set([a['id'] for a in followed])
    top_names = set([a['name'] for a in top])
    top_ids = set([a['id'] for a in top])

    known_artists = followed_names | top_names

    # Getting thew new artists is an expensive operation: cache it
    if os.path.isfile("new-artists.json"):
        with open("new-artists.json") as fartists:
            new_artists = json.load(fartists)

    else:

        # Let's use as seed the artists in top and followed lists
        artists_seed_names = list(followed_names & top_names)
        artists_seed_ids = list(followed_ids & top_ids)

        # We can get related artists: /v1/artists/{id}/related-artists
        new_artists = find_related_artists(token, artists_seed_ids)

        # We can get recommendations: /v1/recommendations
        # seed_artists	A comma separated list of Spotify IDs for seed artists
        new_artists += find_artists_recommendations(token, artists_seed_ids)

        with open("new-artists.json", "w") as fartists:
            json.dump(new_artists, fartists, indent=True)

    # TODO: Remove from new_artists the already followed artists

    new_artists_names = set([a['name'] for a in new_artists])
    print("Total new artists to be checked: ", len(new_artists_names - known_artists))
    print("New artists", (new_artists_names - known_artists))

    return new_artists


def show_recommendations(new_artists):
    """
    Show a report with the artists recommendations

    :param new_artists: dictionary with the artists to analyze
    :return: None
    """

    # In the new_artists dict we can have artists duplicates and also
    # some artist object full and some simplified (without followers)

    artists_followers = {}
    for artist in new_artists:
        if 'followers' in artist:
            if artist['id'] not in artists_followers:
                artists_followers[artist['name']] = artist['followers']['total']

    artists_followers_sorted = sorted(artists_followers.items(), key=operator.itemgetter(1))

    print(json.dumps(artists_followers_sorted, indent=True))



if __name__ == '__main__':
    token = explorer.collect_tokens(SPOTIFY_USER, SCOPES)
    new_artists = find_artists(token)
    # From all new artists select some of them using filters like genre, followers ...
    show_recommendations(new_artists)

