#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# An experimental Spotify Recommeder
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

import json
import os
import time

import requests

import spotipy.util as util

SPOTIFY_API = 'https://api.spotify.com/v1'
SPOTIFY_API_ME = SPOTIFY_API + '/me'

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


def query_api(token, url, method="GET", data=None):
    """
    Send a query to the Spotiy API

    :param token: Auth token
    :param url: URL for the endpoint we want to access
    :return: The result in json format
    """

    # TODO: Control rate limit
    # If status code is 429, Retry-After header field has the seconds to wait
    # Somewhere around 10-20 requests per second would put you in the correct ballpark
    # TODO: Use cache field to avoid querying the API
    # https://developer.spotify.com/web-api/user-guide/#conditional-requests

    headers = {"Authorization": "Bearer %s" % token}
    if method == "GET":
        res = requests.get(url, headers=headers)
    elif method == "POST":
        res = requests.post(url, headers=headers, data=data)
    try:
        res.raise_for_status()
    except Exception:
        print("Error in query to Web API", res.reason, res.text)
        raise

    return res.json()


def find_user_tops(token, kind='tracks'):
    """
    Find the top tracks or artists
    :param token: Auth token
    :return: A tracks or artists list
    """

    kinds = ['tracks', 'artists']

    if kind not in kinds:
        raise RuntimeError('Tops are only available for %s not for %s' % (kinds, kind))

    # Right now the API from Spotify only allows to get the 50 tracks as top
    # Using the artist we can use it as an starting point to find other
    # contents appetizing
    limit = "50"
    top_url = SPOTIFY_API_ME + "/top/%s?limit=%s" % (kind, limit)
    top = query_api(token, top_url)

    return top['items']


def find_user_followed_artists(token):
    """
    Find the artists a user is following
    :param token: Auth token
    :return: An artists list
    """

    artists = []
    after = ''

    limit = 50

    while True:
        time.sleep(0.1)

        followed_url = SPOTIFY_API_ME + "/following?type=artist&limit=%i" % limit
        if after:
            followed_url += "&after=" + after
        items = query_api(token, followed_url)

        artists += items['artists']['items']
        after = items['artists']['cursors']['after']
        if not after:
            break

    return artists

