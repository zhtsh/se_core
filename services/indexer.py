#!/usr/bin/python
# coding=utf8
# author=david

import os
import sys
import logging
from os import path

module_path = path.abspath(path.join(path.dirname(__file__), '../core'))
sys.path.append(module_path)
from core import Indexer


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python indexer.py docs_path')
        sys.exit(1)
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    docs_path = sys.argv[1]
    index_path = path.abspath(path.join(path.dirname(__file__), '../data/index'))
    indexer = Indexer(index_path)
    for dir_name, subdir_list, file_list in os.walk(docs_path):
        for file_path in file_list:
            logging.info('processing doc: %s' % file_path)
            file_path = path.abspath(path.join(docs_path, dir_name, file_path))
            doc = open(file_path, 'rb').read()
            indexer.indexing_doc(doc)
    indexer.save()