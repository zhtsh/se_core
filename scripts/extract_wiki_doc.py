#!/usr/bin/python
# coding=utf8
# author=david

import os
import re
import sys
from os import path

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python extract_wik_doc.py input_path output_path")
        sys.exit(1)
    input_path, output_path = sys.argv[1:]
    doc_start_tag = '<doc id="'
    doc_end_tag = '</doc>\n'
    for dir_name, subdir_list, file_list in os.walk(input_path):
        print('Found directory: %s' % dir_name)
        for fname in file_list:
            fpath = path.abspath(path.join(input_path, dir_name, fname))
            print('Processing file: %s' % fpath)
            content = open(fpath, 'rb').read()
            offset = 0
            while offset < len(content):
                doc_start_pos = content.find(doc_start_tag, offset)
                doc_end_pos = content.find(doc_end_tag, offset)
                if doc_start_pos != -1 and doc_end_pos != -1 and doc_end_pos > doc_start_pos:
                    offset = doc_end_pos + len(doc_end_tag)
                    doc = content[doc_start_pos:offset]
                    matched_result = re.search(r"doc id=\"(\d+)\"", doc)
                    if matched_result:
                        doc_id = matched_result.groups()[0]
                        output_file = path.join(output_path, doc_id)
                        with open(output_file, 'wb') as ofile:
                            ofile.write(doc)
                else:
                    break