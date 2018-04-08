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

from spoting.genius import build_genius_token, find_genius_artist, find_genius_artist_songs, scrap_lyrics

AUTHOR='Mecano'


if __name__ == '__main__':


    # Get the Genius token
    token = build_genius_token()

    print("Finding the lyrics for", AUTHOR)

    # Get the artist id
    artist_id = find_genius_artist(token, AUTHOR)

    # Get the songs for this artists and the lyrics for them
    for song in find_genius_artist_songs(token, artist_id):
        print("New song found", song['title'])

    # Cure the data removing duplicate songs (upper/lower case, larger titles ...

    # And now get the lyrics for the songs
    print("TODO: Get the lyrics for the songs")
