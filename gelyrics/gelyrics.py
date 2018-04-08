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
import argparse
import json
import sys
from time import time

import requests

from spoting.genius import build_genius_token, find_genius_artist, find_genius_artist_songs, scrap_lyrics

def get_params():
    parser = argparse.ArgumentParser(usage="usage: gelyrics.py [options]",
                                     description="Collect songs data for an artist")
    parser.add_argument('-a', '--artist', required=True, help="Name of the artist to collect songs for")
    parser.add_argument('-l', '--lyrics', required=False, action='store_true', help="Collect also the lyrics for the songs")

    return parser.parse_args()

if __name__ == '__main__':

    task_init = time()

    args = get_params()

    artist = args.artist
    lyrics = True if args.lyrics else False

    total_songs = 0

    # Get the Genius token
    token = build_genius_token()

    print("Finding the lyrics for", artist)

    # Get the artist id
    artist_id = find_genius_artist(token, artist)

    if not artist_id:
        print("Can not find %s in Genius" % artist)
        sys.exit(1)

    songs_with_lyrics = []

    # Get the songs for this artists and the lyrics for them
    for song in find_genius_artist_songs(token, artist_id, lyrics=lyrics, unique=True):
        print("New song found", song['title'])
        songs_with_lyrics.append(song)

        # Write the file after each 50 songs so if there are problems we don't loose data
        if total_songs % 50 == 0:
            with open(artist+"_songs.json", "w") as fsongs:
                json.dump(songs_with_lyrics, fsongs, indent=True, ensure_ascii=False)

        total_songs += 1

    # Write all songs to a file
    with open(artist+"_songs.json", "w") as fsongs:
            json.dump(songs_with_lyrics, fsongs, indent=True, ensure_ascii=False)


    print("%i songs collected in %0.3f sec" % (total_songs, time() - task_init))

