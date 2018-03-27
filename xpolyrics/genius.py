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

import requests

from bs4 import BeautifulSoup


GENIUS_API = "https://api.genius.com"
TOKEN_FILE = ".token-genius"

def build_genius_token():
    token = None

    with open(TOKEN_FILE) as ftoken:
        token = ftoken.read()[:-1]

    return token

def scrap_lyrics(lyrics_url):
    page = requests.get(lyrics_url)

    html = BeautifulSoup(page.text, "html.parser")  # Extract the page's HTML as a string
    lyrics = html.find("div", class_="lyrics").get_text()
    return lyrics


if __name__ == '__main__':

    # https://genius.com/api-support Support for using the API

    token = build_genius_token()

    artist = "Mecano"
    song = "Papá cuéntame otra vez"

    url = GENIUS_API + "/search?q=" + artist
    url = GENIUS_API + "/search?q=" + song
    headers = {"Authorization": "Bearer " + token}
    res = requests.get(url, headers=headers)

    lyrics = res.json()

    lyric = lyrics['response']['hits'][0]['result']['path']

    # Lyrics can not be accessed directly from the API
    # https://genius.com/discussions/277279-Get-the-lyrics-of-a-song
    # A URL is included with a web page with the lyrics
    # Scrapping it: http://www.johnwmillr.com/scraping-genius-lyrics/

    lyrics_url = lyrics['response']['hits'][0]['result']['url']

    print(scrap_lyrics(lyrics_url))

    # To embeddthe lyrics on a web page
    # <div id='rg_embed_link_1587003' class='rg_embed_link' data-song-id='1587003'>Read
    # <a href='https://genius.com/Mecano-un-ano-mas-lyrics'>“Un Año Mas” by Mecano</a> on Genius</div>
    # <script crossorigin src='//genius.com/songs/1587003/embed.js'></script>

