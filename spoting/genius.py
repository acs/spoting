from time import time

import requests

from bs4 import BeautifulSoup

# GENIUS config
GENIUS_API = "https://api.genius.com"
TOKEN_FILE = ".token-genius"


def build_genius_token():
    """
    Build a Genius API token. Right now it must be already in a file.

    :return: A Genius Token
    """
    token = None

    with open(TOKEN_FILE) as ftoken:
        token = ftoken.read()[:-1]

    return token


def scrap_lyrics(lyrics_url):
    """
    Scrap the lyrics from Genius HTML lyrics song page. This scrapper must be changed
    when Genius changes the HTML included in the web lyrics song page.

    :param lyrics_url: Genius song URL
    :return: a string with the lyrics for the song
    """
    page = requests.get(lyrics_url)

    # Lyrics can not be accessed directly from the API
    # https://genius.com/discussions/277279-Get-the-lyrics-of-a-song
    # A URL is included with a web page with the lyrics
    # Scrapping it following: http://www.johnwmillr.com/scraping-genius-lyrics/

    html = BeautifulSoup(page.text, "html.parser")  # Extract the page's HTML as a string
    lyrics = html.find("div", class_="lyrics").get_text()
    return lyrics


def embed_lyrics(song_id, song_url, song_title, song_author):
    """
    Build a Genius viewer to show the lyrics of a song

    :param song_id: Genius song id
    :param song_url:  Genius song URL
    :param song_title: Genius song title
    :param song_author: Genius song author
    :return: HTML to be included a web page to show the lyrics in Genius viewer
    """

    embed_viewer = """
    <div id='rg_embed_link_%s' class='rg_embed_link' data-song-id='%s'>
        Read <a href='%s' >%s by %s </a> on Genius.
    </div>
    <script crossorigin src='//genius.com/songs/%s/embed.js'></script>
    """ % (song_id, song_id, song_url, song_title, song_author, song_id)

    return embed_viewer

def find_genius_artist(token, artist_name):
    """

    :param token: Genius user token
    :param artist_name: name of the artists to find
    :return: the Genius artist object
    """

    artist_id = None

    url = GENIUS_API + "/search?q=" + artist_name
    headers = {"Authorization": "Bearer " + token}
    res = requests.get(url, headers=headers)
    res_json = res.json()

    # Time to find the artist from all the results
    # Genius search for the artist_name in all places so some results
    # could not be related to the artist_name, but for a song with the same name than the artist_name
    for item in res_json['response']['hits']:
        artist_found = item['result']['primary_artist']['name']
        if artist_found == artist_name:
            artist_id = item['result']['primary_artist']['id']
            break

    return artist_id




def find_genius_lyrics(token, song_name):
    """
    Find the lyrics of a song in Genius given its name

    :param token: Genius user token
    :param song_name: name of the song to search lyrics for
    :return: lyrics of the song if found
    """

    url = GENIUS_API + "/search?q=" + song_name
    headers = {"Authorization": "Bearer " + token}
    res = requests.get(url, headers=headers)
    lyrics = res.json()

    return lyrics

def find_genius_artist_songs(token, artist_id, lyrics=True, unique=False, full=False):
    """

    :param token:  Genius user token
    :param artist_id: id of the artist to search songs for
    :param lyrics: if True include the lyrics in a new field in the song JSON
    :param unique: if True try to detect deuplicated songs and don't return them
    :param full: if True use the "song" API to get the full data for a song (including album for example)
    :return: list of Genius songs objects
    """

    songs_titles = []
    page = 1
    per_page = 50  # Max number per page

    while True:
        url = GENIUS_API + "/artists/%s/songs?per_page=%i&page=%i" % (artist_id, per_page, page)
        headers = {"Authorization": "Bearer " + token}
        res = requests.get(url, headers=headers)
        res_json = res.json()

        songs = res_json['response']['songs']

        for song in songs:
            if unique:
                if song['title'].lower() in songs_titles:
                    print("Not adding duplicated song:", song['title'])
                    continue
                else:
                    songs_titles.append(song['title'].lower())
            if full:
                url = GENIUS_API + "/songs/%s" % (song['id'])
                headers = {"Authorization": "Bearer " + token}
                res = requests.get(url, headers=headers)
                res_json = res.json()
                song = res_json['response']['song']
            if lyrics:
                task_init = time()
                song['lyrics'] = scrap_lyrics(song['url'])
                print("%s: Total lyrics collecting time ... %0.3f sec" %
                    (song['title'], time() - task_init))

            yield song

        if 'next_page' in res_json['response'] and res_json['response']['next_page']:
            page = res_json['response']['next_page']
        else:
            break


