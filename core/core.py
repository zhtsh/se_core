#!/usr/bin/python
# coding=utf8
# author=david

import re
import json
import math
import logging
from os import path
from nltk.corpus import stopwords
from nltk.stem.lancaster import LancasterStemmer

class Preprocessor(object):
    """
    document preprocessing helper class
    """

    def __init__(self):
        self.stemmer = LancasterStemmer()
        self.english_stopwords = stopwords.words('english')

    def tokenizer(self, text):
        text = text.lower()
        tokens = [token for token in re.split(r'[^0-9a-z]', text) if token]
        return tokens

    def remove_stopword(self, tokens):
        filtered_tokens = [token for token in tokens
                                if token not in self.english_stopwords]
        return filtered_tokens

    def stemming(self, token):
        return self.stemmer.stem(token)

    def preprocessing(self, doc):
        tokens = self.tokenizer(doc)
        tokens = self.remove_stopword(tokens)
        tokens = [self.stemming(token) for token in tokens]
        return tokens

    def tokens2dict(self, tokens):
        token_dict = {}
        for i, token in enumerate(tokens):
            if token not in token_dict:
                token_dict[token] = [0, []]
            token_dict[token][0] += 1
            token_dict[token][1].append(i+1)
        return token_dict


class Indexer(object):
    """
    search engine indexing class
    """

    def __init__(self, index_path=None):
        self.index_path = index_path
        self.inverted_index = {}
        self.docs_index = []
        self.term_id = 0
        self.doc_id = 0
        self.preprocessor = Preprocessor()

    def indexing_doc(self, doc):
        tokens = self.preprocessor.preprocessing(doc)
        token_dict = self.preprocessor.tokens2dict(tokens)
        self.docs_index.append([len(tokens), token_dict])
        for token, tf in token_dict.iteritems():
            if token not in self.inverted_index:
                self.inverted_index[token] = [self.term_id, 0, 0, []]
                self.term_id += 1
            self.inverted_index[token][1] += tf[0]
            self.inverted_index[token][2] += 1
            self.inverted_index[token][3].append([self.doc_id, tf[0], tf[1]])
        doc_path = path.join(self.index_path, '%d.doc' % self.doc_id)
        with open(doc_path, 'wb') as doc_file:
            doc_file.write(doc)
        self.doc_id += 1

    def indexing_docs(self, docs):
        for doc in docs:
            self.indexing_doc(doc)

    def avdl(self):
        total_dl = sum([doc[0] for doc in self.docs_index])
        return (1.0 * total_dl) / self.doc_id

    def save(self):
        index_data_path = path.join(self.index_path, 'index')
        with open(index_data_path, 'wb') as index_file:
            json_data = {}
            json_data['index_path'] = self.index_path
            json_data['inverted_index'] = self.inverted_index
            json_data['docs_index'] = self.docs_index
            json_data['term_id'] = self.term_id
            json_data['doc_id'] = self.doc_id
            index_file.write(json.dumps(json_data))

    @classmethod
    def load(cls, index_data_path):
        indexer = Indexer()
        json_data = json.load(open(index_data_path, 'rb'))
        indexer.index_path = json_data['index_path']
        indexer.inverted_index = json_data['inverted_index']
        indexer.docs_index = json_data['docs_index']
        indexer.term_id = json_data['term_id']
        indexer.doc_id = json_data['doc_id']
        return indexer


class Searcher(object):
    """
    query searching class
    """

    def __init__(self, indexer, mode='BM25', k=1.2, b=0.75):
        self.preprocessor = Preprocessor()
        self.indexer = indexer
        self.mode = mode
        self.k = k
        self.b = b
        self.avdl = self.indexer.avdl()

    def search(self, query, topN=10):
        query_tokens = self.preprocessor.preprocessing(query)
        query_token_dict = self.preprocessor.tokens2dict(query_tokens)
        scores = []
        for doc_id, doc in enumerate(self.indexer.docs_index):
            scores.append((doc_id, self._scoring(query_token_dict, doc)))
        scores.sort(key=lambda item: item[1], reverse=True)
        return scores[:topN]

    def _scoring(self, query, doc):
        score = 0.0
        if self.mode == 'BM25':
            query_terms = set(query.keys())
            doc_terms = set(doc[1].keys())
            matched_tokens = query_terms.intersection(doc_terms)
            for matched_token in matched_tokens:
                query_term_freq = query[matched_token][0]
                doc_term_freq = doc[1][matched_token][0]
                normalized_dl = 1.0 - self.b + self.b * doc[0] / self.avdl
                tf = (self.k + 1.0) * doc_term_freq / (doc_term_freq + self.k * normalized_dl)
                df = self.indexer.inverted_index[matched_token][2]
                idf = math.log((self.indexer.doc_id + 1.0) / df)
                score += (query_term_freq * tf * idf)
        elif self.mode == 'PL2':
            score = 0.0
        return score


class RelevanceFeedback(object):
    """
    query relevance feedback class
    """

    pass