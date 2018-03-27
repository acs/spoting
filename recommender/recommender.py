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
import operator
import os.path


from spoting.spoting import (SPOTIFY_API, SPOTIFY_API_ME,
                             collect_tokens, query_api,
                             find_user_followed_artists, find_user_tops)

DEBUG = True

SPOTIFY_USER = 'acsspotify'
SPOTIFY_MARKET = "es"
SCOPES = 'user-library-read,user-read-recently-played,user-top-read,user-follow-read,playlist-modify-public'
RECOMMENDER_LIST = "Recommender"
ARTIST_RARE_MAX_FOLLOWERS = 5000
RECOMMENDER_RARE_LIST = "RecommenderRare"


def clean_artists(artists, remove=[]):
    """
    Remove duplicates and remove list from an artists list

    :param artists: list of artists to be cleaned
    :param remove: ids of artists to remove
    :return: the new list of artists
    """

    cleaned_artists = []
    already_added_ids = []

    for artist in artists:
        if artist['id'] in remove:
            continue
        elif artist['id'] in already_added_ids:
            continue
        else:
            cleaned_artists.append(artist)
            already_added_ids.append(artist['id'])

    return cleaned_artists


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
        recommend_url = SPOTIFY_API + "/recommendations?limit=%i&%s" % (limit, seed)
        tracks = query_api(token, recommend_url)

        # Now we need to extract the artists from the tracks
        # The artist object included is the simplified one, so no followers info
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
        related_url = SPOTIFY_API + "/artists/%s/related-artists" % (artist_id)
        related_artists = query_api(token, related_url)
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

    followed = find_user_followed_artists(token)
    top = find_user_tops(token, kind='artists')

    followed_names = set([a['name'] for a in followed])
    followed_ids = set([a['id'] for a in followed])
    top_names = set([a['name'] for a in top])
    top_ids = set([a['id'] for a in top])

    known_artists = followed_names | top_names
    known_artists_ids = followed_ids | top_ids

    # Getting thew new artists is an expensive operation: cache it
    if os.path.isfile("new-artists.json"):
        with open("new-artists.json") as artists_file:
            new_artists = json.load(artists_file)
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

    # new_artists_names = set([a['name'] for a in new_artists])
    # print("Total new artists to be checked: ", len(new_artists_names - known_artists))
    # print("New artists", (new_artists_names - known_artists))

    # Clean new_artists: Remove already followed artists and duplicates
    artists = clean_artists(new_artists, list(known_artists_ids))

    return artists


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


def fetch_tracks_ids_from_playlist(playlist_id):

    url_playlist = SPOTIFY_API + "/users/%s/playlists/%s/tracks" % (SPOTIFY_USER, playlist_id)

    already_tracks_ids = []

    # Get the tracks that already exists to not duplicate data
    already_tracks_ids = []
    offset = 0
    limit = 100
    while True:
        url_tracks = url_playlist + "?limit=%i&offset=%i" % (limit, offset)
        tracks = query_api(token, url_tracks)
        if not tracks['items']:
            break
        already_tracks_ids += [track['track']['id'] for track in tracks['items']]
        offset += limit

    return already_tracks_ids


def filter_artists(artists, artists_filter):
    """
    Filter the list of artists using the filter_

    :param artists: Complete list of artists
    :param artists_filter: filter to be applied to select artists
    :return: the list of artists filtered
    """

    supported_filters = ['rare']
    filtered_artists = []

    if artists_filter not in supported_filters:
        print("artists filter not supported", artists_filter)
        return artists

    if artists_filter == 'rare':
        for artist in artists:
            if 'followers' not in artist:
                # print("Followers not included in ", artist['name'])
                continue
            if artist['followers']['total'] <= ARTIST_RARE_MAX_FOLLOWERS:
                filtered_artists.append(artist)

    return filtered_artists


def add_artists_top_track(token, playlist, artists):
    """
    Add the top track from artists to the playlist with id playlist_id

    :param token: User auth token
    :param playlist_id: Id of the playlist in which to add the tracks
    :param artists: List of artists from which to get the tracks
    :return: None
    """

    playlist_id = playlist['id']

    max_artists = 500  # Safe limit
    max_tracks_pack = 100  # Max number of tracks that can be added per call to a playlist

    if DEBUG:
        max_artists = 5

    # To avoid adding duplicate tracks get the current ones
    print("Finding the tracks that are already in the playlist", playlist['name'])
    already_tracks_ids = fetch_tracks_ids_from_playlist(playlist_id)

    # Get first the tracks to be added to the playlist
    print("Finding the tracks to add to the playlist %s from %i artists (one call per each)"
          % (playlist['name'], len(artists)))
    selected_tracks = []
    for artist in artists[0:max_artists]:
        url_top = SPOTIFY_API + "/artists/%s/top-tracks?country=%s" % (artist['id'], SPOTIFY_MARKET)
        tracks = query_api(token, url_top)
        # Get the first track from the top list
        try:
            if tracks['tracks'][0]['id'] not in already_tracks_ids:
                selected_tracks.append(tracks['tracks'][0])
        except IndexError:
            print("%s does not have top tracks" % artist['name'])

    # Add the tracks found to the playlist in 100 packs
    offset = 0
    print("Adding the tracks to the playlist", playlist['name'])

    while offset < len(selected_tracks):
        data = {}
        data["uris"] = [track["uri"] for track in selected_tracks[offset:offset + max_tracks_pack]]
        offset += max_tracks_pack
        url_playlist = SPOTIFY_API + "/users/%s/playlists/%s/tracks" % (SPOTIFY_USER, playlist_id)
        if data["uris"]:
            res = query_api(token, url_playlist, method='POST', data=json.dumps(data))
        else:
            print("No more tracks to add to %s playlist" % playlist['name'])

    print("Added %i tracks to the playlist %s" % (len(selected_tracks), playlist['name']))


def find_user_playlists(token):
    """
    Find all user playlists using scrolling

    :param token: User auth token
    :return: list of playlists
    """

    # Check that the list does not exists yet
    offset = 0
    max_items = 300
    limit = 20
    playlists = []

    while True:
        playlists_url = SPOTIFY_API_ME + "/playlists?limit=%i&offset=%i" % (limit, offset)
        playlists_res = query_api(token, playlists_url)
        if not playlists_res['items'] or offset >= max_items:
            break
        playlists += playlists_res['items']
        offset += limit

    return playlists


def create_playlist(token, name, description=""):
    """
    Creates a new playlist with one song for all the artists

    :param token: User auth token
    :param name: name of the playlist to create
    :return: the playlist created
    """

    playlists = find_user_playlists(token)
    playlist_id = None

    for playlist in playlists:
        if playlist['name'] == name:
            playlist_id = playlist['id']
            break

    if not description:
        description= "Spoting playlist: https://github.com/acs/spoting."

    if not playlist_id:
        # Next create the new mailing list
        create_url = SPOTIFY_API + "/users/%s/playlists" % SPOTIFY_USER
        playlist_data = {
            "name": name,
            "description": description
        }

        playlist = query_api(token, create_url, method="POST", data=json.dumps(playlist_data))
        recommender_list_id = playlist['id']

    return playlist


if __name__ == '__main__':
    token = collect_tokens(SPOTIFY_USER, SCOPES)

    # From all new artists select some of them using filters like genre, followers ...
    new_artists = find_artists(token)
    # show_recommendations(new_artists)

    # Create a new playlist with one song for each of the new artists
    description = "Spoting playlist with one song for the recommended new artists: https://github.com/acs/spoting."
    playlist = create_playlist(token, RECOMMENDER_LIST, description)
    # Time to find the tracks and add them to the playlist
    add_artists_top_track(token, playlist, new_artists)

    # Create a new playlist with one song for each of the new rare artists
    description = "Spoting playlist with one song for the recommended new RARE artists: https://github.com/acs/spoting."
    playlist = create_playlist(token, RECOMMENDER_RARE_LIST, description)
    # Time to find the tracks and add them to the playlist
    artists_rare = filter_artists(new_artists, 'rare')
    add_artists_top_track(token, playlist, artists_rare)

