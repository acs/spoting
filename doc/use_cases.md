# Use Cases for Spotify Web API

An open document with use cases and ideas on how to do cool things with the Spotity Web API.

All in pre-alpha status just for my personal usage now. But willing to improve it and to collaborate with others.

I will just add new use cases as they come to my mind. No order yet. No action plan. Just a place in which to write things.

## Done

### Finding new artists to follow

https://github.com/acs/spoting/issues/1

Implemented in: [recommender.py](https://github.com/acs/spoting/blob/master/explorer/recommender.py) 

Spotify clients already recommends you new artists using playlists.
But probably having in mind my own criteria I could do a better job for me.

The analysis of the artists that I already follow can be used as the seed
for getting recommendations from Spotify, and the use this recommendations as
seed for new recommendations until for example, 1000 artists are found.

In the current implementation only the first circle is covered: related artists to my followed and top artists.

In the current implementation, one top track is fetch from each of the related artists
and it is added to a playlist called "Recommender".

Another playlist "RecommenderRare" is created using the artists which are followed by less than 5000 listeners.

The natural extension for this use case is to filter the new artists with different criteria: genres, popularity,  


## Pending

### Understading music charms

https://github.com/acs/spoting/issues/2

Why I like some kind of music and not others? What are the genres of music that I like more?

Not just talking about rock, pop, metal, jazz but try to find more specific genres that I like.

Also, Spotify does [analysis in tracks](https://developer.spotify.com/web-api/get-audio-analysis/). 
Is it possible from the to understand whan hve in common by most beloved songs? 


### Finding new genders of music I like and the relation between them

### Tracking new releases of music that I must listen to

### Understanding the relationships between artists

### Understanding the evolution of the artists

### Understanding the relevance of the artists

### Tracking the history of the music based on genres

What was the first rock song? How was it created? How rock artists evolve?

What are the genres more active now? And the genres that are decaying? 

How a new genre appears?

### Comparing Artists

### Track copyright issues in music

### Music Trends

Coudl we get trends from the API? I have not seen for example if it is possible 
to get the evolution of followers for an artists.

### Analyze specific moments like the 80's in Spain
  

### Read Spotify Insights 

[Spotify Insights](https://insights.spotify.com) has a lot of interesting use cases to get inspired.
