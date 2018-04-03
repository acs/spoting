from spoting.spoting import collect_tokens, find_user_playlists, find_user_playlist_tracks


def find_track_lyric(token, track):
    """
    Find lyrics for a track

    :param token: Genius auth token
    :param track: track to be searched in Genius for its lyrics
    :return: the lyrics for the track
    """

    lyrics = ""

    return lyrics


class TracksData():

    def __init__(self, state):
        self.state = state

    def fetch(self):
        if not self.state or self.state.is_empty():
            return
        elif self.state.playlists:
            tracks = find_user_playlist_tracks(self.state.playlists)
            for track in tracks:
                yield track


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
            for playlist in self.state.playlists:
                yield playlist


class LyricsData():

    def __init__(self, state=None):
        self.state = state

    def fetch(self):
        if not self.state or self.state.is_empty():
            return
        elif self.state.tracks:
            for track in self.state.tracks:
                yield find_track_lyric(track)


class LyricsDataData():

    def __init__(self, state=None):
        self.state = state

    def fetch(self):
        for metric_data in MetricData.objects.all():
            yield metric_data
