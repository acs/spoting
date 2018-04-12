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
#   Alvaro del Castillo <acs@bitergia.com>
#
import argparse
import json
import string

from pprint import pprint

from elasticsearch import helpers, Elasticsearch

from nltk import word_tokenize, PorterStemmer, collections
from nltk.corpus import stopwords
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer


def get_params():
    parser = argparse.ArgumentParser(usage="usage: clusongs.py [options]",
                                     description="Automatic Clustering of songs")
    parser.add_argument('-d', '--dataset', required=True, help="File path with the songs")
    parser.add_argument('-e', '--elasticsearch_url', required=False, default='http://localhost:9200',
                        help="Elasticsearch URL")
    parser.add_argument('-i', '--elasticsearch_index', required=False, default='songs_clusters',
                        help="Elasticsearch index in which to store the results")

    return parser.parse_args()


def process_text(text, stem=True):
    """ Tokenize text and stem words removing punctuation """
    table = str.maketrans({key: None for key in string.punctuation})
    text = text.translate(table)
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


def feed_songs(songs, es_url, es_index):
    """
    Feed the songs to a Elasticsearch index

    :param songs:  JSON document with the list of songs to feed to Elasticsearch
    :param es_url:  Elasticsearch URL
    :param es_index: Elasticsearch index
    :return: True is all goes well
    """

    es_conn = Elasticsearch([es_url], timeout=100)
    docs = []

    # Uploading info to the new ES
    for item in songs:
        item_id = item['id']
        doc = {
            "_index": es_index,
            "_type": "item",
            "_id": item_id,
            "_source": item
        }
        docs.append(doc)
    helpers.bulk(es_conn, docs)
    print("Items written to Elasticsearch: " + str(len(docs)))


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

    args = get_params()

    with open(args.dataset) as f:
        songs_json = json.load(f)

    lyrics = []
    titles = []
    for song in songs_json:
        lyrics.append(song['lyrics'])
        titles.append(song['title'])

    print("Lyrics read: %i" % len(lyrics))

    clusters = cluster_texts(lyrics, 10)

    clusters_with_titles = {}
    for cluster_id, song_pos_list in clusters.items():
        cluster_song_list = []
        for song_pos in song_pos_list:
            cluster_song_list.append(titles[song_pos])
            songs_json[song_pos]['cluster'] = int(cluster_id)

        clusters_with_titles[cluster_id] = cluster_song_list

    pprint(clusters_with_titles)

    feed_songs(songs_json, args.elasticsearch_url, args.elasticsearch_index)

    print("Songs with cluster information uploaded to", args.elasticsearch_url + "/" + args.elasticsearch_index)
