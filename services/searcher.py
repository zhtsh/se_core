#!/usr/bin/python
# coding=utf8
# author=david

import sys
from os import path
from datetime import date
import tornado.escape
import tornado.ioloop
import tornado.web
import tornado.gen
import tornado.httpclient

module_path = path.abspath(path.join(path.dirname(__file__), '../core'))
sys.path.append(module_path)
from core import Indexer, Searcher

class IndexHandler(tornado.web.RequestHandler):

    def get(self):
        response = {
            'version' : '1.0.1',
            'last_build' : date.today().isoformat()
        }
        self.write(response)

class SearchHandler(tornado.web.RequestHandler):

    def get(self):
        try:
            query = self.get_query_argument('q')
        except Exception as e:
            logging.error(str(e))
            self.write({'results': []})
            return
        results = searcher.search(query)
        response = {
            'results': [{'doc_id': doc_id, 'score': score} for doc_id, score in results]
        }
        self.write(response)

def make_app():
    return tornado.web.Application([
        (r"/", IndexHandler),
        (r"/search", SearchHandler),
    ])

if __name__ == '__main__':
    import logging
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    index_data_path = path.abspath(path.join(path.dirname(__file__), '../data/index/index'))
    logging.info('loading index data...')
    indexer = Indexer.load(index_data_path)
    logging.info('creating Searcher instance...')
    searcher = Searcher(indexer)
    app = make_app()
    app.listen(9999)
    tornado.ioloop.IOLoop.current().start()
