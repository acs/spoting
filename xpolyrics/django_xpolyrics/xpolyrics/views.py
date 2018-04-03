import functools
import json

from datetime import datetime
from time import time

from django import shortcuts
from django.http import Http404

from django.http import HttpResponse
from django.template import loader

from spoting.spoting import collect_tokens
from spoting.genius import embed_lyrics

from . import forms
from . import data

# TODO: OAuth2 web integration must retrieve this data
# SPOTIFY config
SPOTIFY_USER = 'acsspotify'
SPOTIFY_MARKET = "es"
SCOPES = 'user-library-read'


#
# Logic not moved inside classes yet
#

def perfdata(func):
    @functools.wraps(func)
    def decorator(*args, **kwargs):
        task_init = time()
        data = func(*args, **kwargs)
        print("%s: %0.3f sec" % (func, time() - task_init))
        return data
    return decorator


@perfdata
def build_forms_context(state=None):
    """
    Build PlayLists, Tracks and Lyrics Viewer Forms

    :param state: state for the forms
    :return: forms created as a dictionary
    """

    spotify_token = collect_tokens(SPOTIFY_USER, SCOPES)

    if not state:
        state = EditorState(spotify_token=spotify_token)
    else:
        state.spotify_token = spotify_token


    playlists_form = forms.PlaylistsForm(state=state)
    tracks_form = forms.TracksForm(state=state)
    lyrics = None

    if state:
        if state.playlists:
            playlists_form.initial['id'] = state.playlists[0]
        if state.tracks:
            tracks_form.initial['id'] = state.tracks[0]
            genius_data = next(data.LyricsData(state).fetch())
            song_data = genius_data['response']['hits'][0]['result']
            song_id = song_data['id']
            song_url = song_data['url']
            song_title = song_data['title']
            song_author = song_data['primary_artist']['name']

            lyrics = embed_lyrics(song_id, song_url, song_title, song_author)

    context = {
               "playlists_form": playlists_form,
               "tracks_form": tracks_form,
               "lyrics": lyrics
               }
    return context


@perfdata
def index(request):
    """ Shows the XpoLyrics Viewer """

    context = build_forms_context()

    return shortcuts.render(request, 'xpolyrics/editor.html', context)


@perfdata
def select_playlist(request):
    """ Select a playlist to show its tracks """

    spotify_token = collect_tokens(SPOTIFY_USER, SCOPES)

    context = build_forms_context(EditorState(spotify_token=spotify_token))

    return shortcuts.render(request, 'xpolyrics/editor.html', context)



def return_error(message):

    template = loader.get_template('xpolyrics/error.html')
    context = {"alert_message": message}
    render_error = template.render(context)
    return HttpResponse(render_error)

#
# Classes implementing the logic
#


class EditorState():

    def __init__(self, playlists=None, tracks=None, lyrics=None, form=None, spotify_token=None, genius_token=None):
        self.spotify_token = spotify_token
        self.genius_token = genius_token
        self.playlists = playlists
        self.tracks = tracks
        self.lyrics = lyrics

        if form:
            # The form includes the state not changed to be propagated
            playlists_state = form.cleaned_data['playlists_state']
            tracks = form.cleaned_data['tracks_state']

            if self.playlists is None:
                self.playlists = [playlists_state] if playlists_state else []
            if self.tracks is None:
                self.tracks = [tracks] if tracks else []
            if self.lyrics is None:
                self.lyrics = [lyrics] if lyrics else []

    def is_empty(self):
        return not (self.playlists or self.tracks)

    def initial_state(self):
        """ State to be filled in the forms so it is propagated

        The state needs to be serialized so it can be used in
        forms fields.
        """
        initial = {}

        if self.playlists:
            initial['playlists_state'] = ";".join([str(pid) for pid in self.playlists])
        else:
            initial['playlists_state'] = None

        if self.tracks:
            initial['tracks_state'] = ";".join([str(tid) for tid in self.tracks])
        else:
            initial['tracks_state'] = None

        return initial


class TrackView():

    @staticmethod
    def select_track(request, context=None):
        error = None
        template = 'xpolyrics/editor.html'
        if request.method == 'POST':
            spotify_token = collect_tokens(SPOTIFY_USER, SCOPES)
            state = EditorState(spotify_token=spotify_token, tracks=[request.POST['id']])
            form = forms.TracksForm(request.POST, state=state)
            if form.is_valid():
                attr_id = form.cleaned_data['id']
                tracks = [attr_id] if attr_id else []
                old_tracks = form.cleaned_data['tracks_state']
                if old_tracks == attr_id:
                    # Unselect the track
                    form.cleaned_data['tracks_state'] = None
                    tracks = None
                state = EditorState(form=form, tracks=tracks)

                return shortcuts.render(request, template,
                                        build_forms_context(state))
            else:
                state = EditorState(form=form)
                error = form.errors

            if context:
                context.update(build_forms_context(state))
            else:
                context = build_forms_context(state)

            context.update({"errors": error})
            return shortcuts.render(request, template, context)

        else:
            return shortcuts.render(request, template, build_forms_context())


class PlaylistView():

    @staticmethod
    def select_playlist(request, context=None):
        error = None
        template = 'xpolyrics/editor.html'
        if request.method == 'POST':
            spotify_token = collect_tokens(SPOTIFY_USER, SCOPES)
            spotify_state = EditorState(spotify_token=spotify_token)
            form = forms.PlaylistsForm(request.POST, state=spotify_state)
            if form.is_valid():
                old_playlists = form.cleaned_data['playlists_state']
                playlist_id = form.cleaned_data['id']
                playlists = [playlist_id]
                if old_playlists == playlist_id:
                    # Unselect the playlist and its tracks and lyrics
                    form.cleaned_data['playlists_state'] = None
                    form.cleaned_data['tracks_state'] = None
                    playlists = None
                state = EditorState(playlists=playlists, form=form)
            else:
                state = EditorState(form=form)
                error = form.errors

            if context:
                context.update(build_forms_context(state))
            else:
                context = build_forms_context(state)

            context.update({"errors": error})
            return shortcuts.render(request, template, context)

        else:
            return shortcuts.render(request, template, build_forms_context())
