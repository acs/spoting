#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# An experimental Spotify Playlists Lyrics viewer based on Genius
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

import requests

from bs4 import BeautifulSoup

from spoting.spoting import collect_tokens, find_user_playlists, find_user_playlist_tracks

# SPOTIFY config
SPOTIFY_USER = 'acsspotify'
SPOTIFY_MARKET = "es"
SCOPES = 'user-library-read'

# GENIUS config
GENIUS_API = "https://api.genius.com"
TOKEN_FILE = ".token-genius"

# LIMITS
MAX_PLAY_LISTS = 10
MAX_TRACKS = 50

def build_genius_token():
    token = None

    with open(TOKEN_FILE) as ftoken:
        token = ftoken.read()[:-1]

    return token

def scrap_lyrics(lyrics_url):
    """
    Scrap the lyrics from Genius HTML lyrics song page. This scrapper must be changed
    when Genius changes the HTML included in the web lyrics song page.

    :param lyrics_url: Genius song URL
    :return: a string with the lyrics for the song
    """
    page = requests.get(lyrics_url)

    # Lyrics can not be accessed directly from the API
    # https://genius.com/discussions/277279-Get-the-lyrics-of-a-song
    # A URL is included with a web page with the lyrics
    # Scrapping it following: http://www.johnwmillr.com/scraping-genius-lyrics/

    html = BeautifulSoup(page.text, "html.parser")  # Extract the page's HTML as a string
    lyrics = html.find("div", class_="lyrics").get_text()
    return lyrics


def embed_lyrics(song_id, song_url, song_title, song_author):
    """
    Build a Genius viewer to show the lyrics of a song

    :param song_id: Genius song id
    :param song_url:  Genius song URL
    :param song_title: Genius song title
    :param song_author: Genius song author
    :return: HTML to be included a web page to show the lyrics in Genius viewer
    """

    embed_viewer = """
    <div id='rg_embed_link_%s' class='rg_embed_link' data-song-id='%s'>
        Read <a href='%s' >%s by %s </a> on Genius.
    </div>
    <script crossorigin src='//genius.com/songs/1587003/embed.js'></script>
    """ % (song_id, song_id, song_url, song_title, song_author)

    return embed_viewer


if __name__ == '__main__':

    # The first step is to get the list of Play Lists from Spotify
    token = collect_tokens(SPOTIFY_USER, SCOPES)

    print("Finding the user playlists in Spotify")
    playlists = find_user_playlists(token, MAX_PLAY_LISTS)

    # Get the tracks for all playlists
    print("Getting the tracks for the user playlists in Spotify")
    tracks = []
    for playlist in playlists[0:MAX_PLAY_LISTS]:
        tracks += find_user_playlist_tracks(token, playlist)
        if len(tracks) > MAX_TRACKS:
            break

    # Search the lyrics for the tracks in Genius
    lyrics_found = 0
    lyrics_not_found = 0
    token = build_genius_token()

    print("Finding the lyrics")
    for track in tracks[0:MAX_TRACKS]:
        song = track['track']['name']
        author = track['track']['artists'][0]['name']
        print("Finding the lyrics for %s by %s" % (song, author))

        url = GENIUS_API + "/search?q=" + song
        headers = {"Authorization": "Bearer " + token}
        res = requests.get(url, headers=headers)

        lyrics = res.json()

        if not lyrics['response']['hits']:
            print("Can not find lyrics for %s by %s" % (song, author))
            lyrics_not_found += 1
            continue

        lyrics_found += 1


        lyrics_url = lyrics['response']['hits'][0]['result']['url']

        print(scrap_lyrics(lyrics_url))

    print("Lyrics found/not found: %i/%i" % (lyrics_found, lyrics_not_found))