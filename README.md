# Spoting

This is an experimental project for playing with the Spotify API.

Don't expect to find really useful things here yet, but you can try ;)

## [Explorer](explorer)

[Use Case](https://github.com/acs/spoting/blob/master/doc/use_cases.md#general-explorer)


The initial script I used to understand the Spotify API and howto use it.

`PYTHONPATH=. explorer/explorer.py`


## [Recommender](recommender)

[Use Case](https://github.com/acs/spoting/blob/master/doc/use_cases.md#finding-new-artists-to-follow)

An script to generate playlists in Spotify from recommended artists for the user. 

`PYTHONPATH=. recommender/recommender.py`

## [Lyrics Viewer](xpolyrics)

[Use Case](https://github.com/acs/spoting/blob/master/doc/use_cases.md#lyrics-viewer)

An script to show the lyrics from Spotify playlists.

`PYTHONPATH=. xpolyrics/xpolyrics.py`


## [Spoting library](spoting)

Library with shared methods between the above scripts.

## Authentication
 
You need to have a registered application in Spotify and to add its data to the file **app-credentials.json**.
Use app-credentials-sample.json as a template for it.

You need also a Spotify registered user. The first time you start a script it will use your app config and it will open a web browser so you can login in Spotify.


## References 

* https://github.com/spotify/web-api
* https://developer.spotify.com/web-api
* https://beta.developer.spotify.com/documentation/web-api/
