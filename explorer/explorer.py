#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# An experimental Spotify Data Explorer
#
# Copyright (C) Alvaro del Castillo
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


import time

from spoting.spoting import (SPOTIFY_API, SPOTIFY_API_ME,
                             collect_tokens, query_api,
                             find_user_followed_artists, find_user_tops,
                             )

SPOTIFY_USER = 'acsspotify'
SPOTIFY_MARKET = 'ES'
SCOPES = 'user-library-read,user-read-recently-played,user-top-read,user-follow-read'


def find_playlists(token):
    """
    Get the playlists for the user

    :param token: Auth token
    :return: A playlists list
    """
    url = SPOTIFY_API_ME + "/playlists"

    playlists = query_api(token, url)

    return playlists['items']


def show_artists(artists, title="TRACKS LIST"):
    """
    Print a list of artists in a common format

    :param artists: List of artists to be printed
    :return: None
    """
    # print("\n* %s: name artist" % title)
    print("\n{0:40} {1}\n".format("* " + title + " Track name", "Artist"))
    for artist in artists:
        print("{0:40}".format(artist['name'][0:40]))


def show_tracks(tracks, title="TRACKS LIST"):
    """
    Print a list of track in a common format

    :param tracks: List of tracks to be printed
    :return: None
    """
    # print("\n* %s: name artist" % title)
    print("\n{0:40} {1}\n".format("* " + title + " Track name", "Artist"))
    for track in tracks:
        if 'track' in track:
            track = track['track']
        print("{0:40} {1}".format(track['name'][0:40], track['artists'][0]['name']))


def find_recently_played_tracks(token):
    """
    Find the last 50 find_recently_played_tracks tracks by the user

    :param token: Auth token
    :return: A tracks list
    """

    # Right now the API from Spotify only allows to get the 50 tracks last played
    limit = "50"
    history_url = SPOTIFY_API_ME + "/player/recently-played?limit=%s" % limit
    recent_tracks = query_api(token, history_url)

    return recent_tracks['items']


def search_artist_tracks(token, artist):
    """
    Search tracks for an artist

    :param token: Auth token
    :param artist: Name of the artist to be searched
    :return: A tracks list
    """

    tracks = []
    offset = 0

    limit = 50
    max_items = limit * 5  # Max number of result items to retrieve
    # Maximum offset: 100.000.
    while True:
        time.sleep(0.1)
        search_url = SPOTIFY_API + "/search?type=track&q=artist:%s&limit=%i&offset=%i" % (artist, limit, offset)
        items = query_api(token, search_url)
        if not items['tracks']['items'] or offset >= max_items:
            break
        tracks += items['tracks']['items']
        offset += limit

    return tracks


def find_user_saved_tracks(token):
    """
    Get a list of the songs saved in the current Spotify user’s “Your Music” library.

    :param token: Auth token
    :return: A tracks list
    """

    tracks = []
    offset = 0

    limit = 50
    max_items = limit * 10  # Max number of result items to retrieve
    while True:
        time.sleep(0.1)
        saved_url = SPOTIFY_API_ME + "/tracks?limit=%i&offset=%i" % (limit, offset)
        items = query_api(token, saved_url)
        if not items['items'] or offset >= max_items:
            break
        tracks += items['items']
        offset += limit

    return tracks


if __name__ == '__main__':
    token = collect_tokens(SPOTIFY_USER, SCOPES)
    show_artists(find_user_tops(token, kind='artists'), title="Top")
    show_artists(find_user_followed_artists(token), title="Followed")
    show_tracks(find_user_tops(token), title="Top")
    show_tracks(find_recently_played_tracks(token), title="Recently Played")
    show_tracks(search_artist_tracks(token, "Mecano"))
    show_tracks(find_user_saved_tracks(token))
