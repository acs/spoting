#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# An experimental Spotify Data Explorer
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
import os
import requests
import time

import spotipy.util as util

SPOTIFY_API = 'https://api.spotify.com/v1'
SPOTIFY_API_ME = SPOTIFY_API + '/me'
SPOTIFY_USER = 'acsspotify'
SCOPES = 'user-library-read,user-read-recently-played,user-top-read'

TOKEN_FILE = '.token'


def collect_tokens(user, scopes):
    """
    Get a valid token for a user an a comma separated string list of scopes

    :param user: Spotify user for getting the token
    :param scopes: comma separated string list of scopes
    :return: a token for this user
    """

    # First step is to configure the env for asking for tokens
    with open("app-credentials.json") as file:
        os.environ.update(json.load(file))

    # Access tokens expire after one hour. This expiry time is set on Spotify's side and can't be changed by the client
    # So we ask for a new token if we don't have a recent one

    refresh_token = False

    try:
        # If tokens are older than 1h (3600s) we must refresh them
        if int(time.time() - int(os.path.getmtime(TOKEN_FILE))) > 3600:
            refresh_token = True
    except Exception as ex:
        refresh_token = True

    if refresh_token:
        print("Refreshing the token ... be patient")
        token = util.prompt_for_user_token(user, scopes)
        with open(TOKEN_FILE, "w") as ftoken:
            ftoken.write(token)
    else:
        with open(TOKEN_FILE, "r") as ftoken:
            token = ftoken.read()

    return token


def query_api(token, url):
    """
    Send a query to the Spotiy API

    :param token: Auth token
    :param url: URL for the endpoint we want to access
    :return: The result in json format
    """

    headers = {"Authorization": "Bearer %s" % token}
    res = requests.get(url, headers=headers)
    res.raise_for_status()

    return res.json()


def find_playlists(token):
    """
    Get the playlists for the user

    :param token: Auth token
    :return: A playlists list
    """
    url = SPOTIFY_API_ME + "/playlists"

    playlists = query_api(token, url)

    return playlists['items']


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


def find_tops_tracks(token, kind='tracks'):
    """
    Find the top tracks or artists
    :param token: Auth token
    :return: A tracks list
    """

    # Right now the API from Spotify only allows to get the 50 tracks as top
    limit = "50"
    top_url = SPOTIFY_API_ME + "/top/%s?limit=%s" % (kind, limit)
    top_tracks = query_api(token, top_url)

    return top_tracks['items']


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


if __name__ == '__main__':
    token = collect_tokens(SPOTIFY_USER, SCOPES)
    show_tracks(find_tops_tracks(token), title="Top")
    show_tracks(find_recently_played_tracks(token), title="Recently Played")
    show_tracks(search_artist_tracks(token, "Mecano"))
