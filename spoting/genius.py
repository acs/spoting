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

