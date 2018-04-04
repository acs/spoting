# XpoLyrics Web Application

This is a Django web application to show the lyrics from your tracks in Spotify playlists.

It is an experimental application so it is in alpha status.


## Execution

You need to create three files for authentication issues:

* app-credentials.json: Your spotify app credentials
* .token: your Spotify access token
* .token-genius: your Genius access token

To start the application once you have installed all Python dependencies:

```
PYTHONPATH=../..:. python manage.py runserver
```

and you can access the application in:

http://localhost:8000/xpolyrics/

Just select one of your Spotify playlists, then a track in it and the lyrics must be shown.


## Requirements

* Python >=3.4
* setuptools
* django
* requests

## ROADMAP

There is no ROADMAP for this application. It is just a playground.

## License

Licensed under GNU General Public License (GPL), version 3 or later.
