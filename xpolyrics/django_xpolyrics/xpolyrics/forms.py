import functools

from time import time

from django import forms

from . import data

SELECT_LINES = 20
MAX_ITEMS = 1000  # Implement pagination if there are more items


def perfdata(func):
    @functools.wraps(func)
    def decorator(self, *args, **kwargs):
        task_init = time()
        data = func(self, *args, **kwargs)
        print("%s: Total data collecting time ... %0.3f sec" %
              (self.__class__.__name__, time() - task_init))
        return data
    return decorator


class XpoLyricsForm(forms.Form):

    select_widget = forms.Select(attrs={'size': SELECT_LINES, 'class': 'form-control'})
    attrs = {'size': SELECT_LINES, 'class': 'form-control', 'onclick': 'this.form.submit()'}
    select_widget_onclick = forms.Select(attrs=attrs)

    # Hidden widgets to store the state of the XpoLyricsForm
    playlists_state = forms.CharField(required=False, max_length=50, widget=forms.HiddenInput())
    tracks_state = forms.CharField(required=False, max_length=50, widget=forms.HiddenInput())
    lyrics_state = forms.CharField(required=False, max_length=50, widget=forms.HiddenInput())

    def is_empty_state(self):
        return self.state.is_empty() if self.state else True

    def __init__(self, *args, **kwargs):
        self.state = kwargs.pop('state') if 'state' in kwargs else None
        if self.state:
            if 'initial' in kwargs:
                kwargs['initial'].update(self.state.initial_state())
            else:
                kwargs['initial'] = self.state.initial_state()
        super(XpoLyricsForm, self).__init__(*args, **kwargs)

        self.state_fields = [self['playlists_state'],
                             self['tracks_state'],
                             self['lyrics_state']
                             ]


class PlaylistsForm(XpoLyricsForm):

    @perfdata
    def __init__(self, *args, **kwargs):
        super(PlaylistsForm, self).__init__(*args, **kwargs)

        choices = ()

        for playlist in data.PlaylistsData(self.state).fetch():
            if (playlist['id'], playlist['name']) not in choices:
                choices += ((playlist['id'], playlist['name']),)

        choices = sorted(choices, key=lambda x: x[1])
        self.fields['id'] = forms.ChoiceField(label='Playlists',
                                              widget=self.select_widget_onclick, choices=choices)


class TracksForm(XpoLyricsForm):

    def list_choices(self):
        choices = ()

        for track in data.TracksData(self.state).fetch():
            if 'track' in track:
                track = track['track']
            if (track['id'], track['name']) not in choices:
                choices += ((track['id'], track['name']),)

        choices = sorted(choices, key=lambda x: x[1])

        return choices

    @perfdata
    def __init__(self, *args, **kwargs):
        super(TracksForm, self).__init__(*args, **kwargs)

        self.fields['id'] = forms.ChoiceField(label='Tracks',
                                              widget=self.select_widget_onclick, choices=self.list_choices())
