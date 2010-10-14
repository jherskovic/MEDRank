#!/usr/bin/env python
# encoding: utf-8
"""
concept_cache.py

Runs the Concept caching system (requires web.py)
Pass the port on which to run the server as the first command-line argument, and 
the location of the cache as the second (defaults to the default cache location)

Created by Jorge Herskovic on 2010-10-11.
Copyright (c) 2010 UTHSC School of Health Information Sciences. All rights reserved.
"""

import sys
import os
import web
import cPickle as pickle
import traceback
import urllib2
from urllib import urlencode
from MEDRank.file.disk_backed_dict import StringDBDict, DatabaseError
from MEDRank.utility.logger import logging, ULTRADEBUG
from MEDRank.utility import cache

urls=("/([c|C]\d+)", "ConceptRecord")
app = web.application(urls, globals())
DEFAULT_CACHE_PORT=8082
DEFAULT_CACHE_HOST="http://127.0.0.1:%d" % DEFAULT_CACHE_PORT
_DEFAULT_CONCEPT_STORAGE=os.path.join(sys.exec_prefix, "medrank_data",
                                      "umls_concepts.db")

class ConceptRecord(object):
    """Serves concepts via a RESTful API"""
    def __init__(self):
        try:
            self._cache_location=sys.argv[2]
        except IndexError:
            self._cache_location=_DEFAULT_CONCEPT_STORAGE
        self._cache=StringDBDict(self._cache_location, file_mode="r")
        
    def GET(self, concept_id):
        web.header('Content-type', 'application/octet-stream')
        try:
            record=self._cache[str(concept_id)]
        except:
            record=None
            print >>sys.stderr, "Error when retrieving %r. Traceback follows." \
                    % concept_id
            print >>sys.stderr, traceback.format_exc()
        return pickle.dumps(record, pickle.HIGHEST_PROTOCOL)
    
    def POST(self, concept_id):
        record=web.input().record
        record=pickle.loads(str(record))
        self._cache[str(pubmed_id)]=record
        return
        
class Client(object):
    """Meant to be imported from other modules to interact with the server."""
    def __init__(self, server_url):
        self._my_server_url=server_url
    def get_record(self, record_id):
        url="%s/%s" % (self._my_server_url, record_id)
        record=urllib2.urlopen(url).read()
        record=pickle.loads(record)
        if record is None:
            raise KeyError("No concept under id %r", record_id)
        return record
    def put_record(self, record_num, data):
        url="%s/%s" % (self._my_server_url, record_num)
        url_data=urlencode({"record": pickle.dumps(data)})
        urllib2.urlopen(url, url_data)
        return 

if __name__ == '__main__':
    app.run()

