from spoting.spoting import fetch_playlists_from_ids, fetch_tracks_from_ids, find_user_playlists, find_user_playlist_tracks
from spoting.genius import build_genius_token, find_genius_lyrics


class PlaylistsData():

    MAX_PLAY_LISTS = 5

    def __init__(self, state):
        self.state = state

    def fetch(self):
        if not self.state or self.state.is_empty():
            print("Finding the user playlists in Spotify")
            for playlist in find_user_playlists(self.state.spotify_token, self.MAX_PLAY_LISTS):
                yield playlist
        elif self.state.playlists:
            for playlist in fetch_playlists_from_ids(self.state.spotify_token, self.state.playlists):
                yield playlist

class TracksData():

    def __init__(self, state):
        self.state = state

    def fetch(self):
        if not self.state or self.state.is_empty():
            return
        elif self.state.playlists:
            tracks = find_user_playlist_tracks(self.state.spotify_token, playlist_id=self.state.playlists[0])
            for track in tracks:
                yield track
        elif self.state.tracks:
            tracks = fetch_tracks_from_ids(self.state.spotify_token, self.state.tracks)
            for track in tracks:
                yield track


class LyricsData():

    def __init__(self, state=None):
        self.state = state

    def fetch(self):
        if not self.state or self.state.is_empty():
            return
        elif self.state.tracks:
            genius_token = build_genius_token()
            # Get only the lyrics for the first track
            tracks = fetch_tracks_from_ids(self.state.spotify_token, [self.state.tracks[0]])
            for track in tracks:
                yield find_genius_lyrics(genius_token, track['name'])
