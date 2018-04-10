#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) Alberto Pérez García-Plaza
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
#   Alberto Pérez García-Plaza <alpgarcia@bitergia.com>
#
import json
import string
from pprint import pprint

from nltk import word_tokenize, PorterStemmer, collections
from nltk.corpus import stopwords
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer


def process_text(text, stem=True):
    """ Tokenize text and stem words removing punctuation """
    text = text.translate(string.punctuation)
    tokens = word_tokenize(text)

    if stem:
        stemmer = PorterStemmer()
        tokens = [stemmer.stem(t) for t in tokens]

    return tokens


def cluster_texts(texts, clusters=3):
    """ Transform texts to Tf-Idf coordinates and cluster texts using K-Means """
    vectorizer = TfidfVectorizer(tokenizer=process_text,
                                 stop_words=stopwords.words('english'),
                                 max_df=0.5,
                                 min_df=0.1,
                                 lowercase=True)

    tfidf_model = vectorizer.fit_transform(texts)
    km_model = KMeans(n_clusters=clusters)
    km_model.fit(tfidf_model)

    clustering = collections.defaultdict(list)

    for idx, label in enumerate(km_model.labels_):
        clustering[label].append(idx)

    return clustering

if __name__ == '__main__':
    # Explore some clustering functionalities.
    # Following links have been used:
    # * https://nlpforhackers.io/recipe-text-clustering/
    #
    # Requirements:
    #   >>> import nltk
    #   >>> nltk.download('punkt')
    #   >>> nltk.download('stopwords')
    #
    with open('../datasets/bob_dylan_songs.json') as f:
        songs_json = json.load(f)

    lyrics = []
    titles = []
    for song in songs_json:
        lyrics.append(song['lyrics'])
        titles.append(song['title'])

    print("Lyrics read: %i" % len(lyrics))

    clusters = cluster_texts(lyrics, 10)

    clusters_with_titles = {}
    for cluster_id, song_id_list in clusters.items():
        cluster_song_list = []
        for song_id in song_id_list:
            cluster_song_list.append(titles[song_id])

        clusters_with_titles[cluster_id] = cluster_song_list

    pprint(clusters_with_titles)