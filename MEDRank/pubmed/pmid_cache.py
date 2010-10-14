#!/usr/bin/env python
# encoding: utf-8
"""
pmid_cache.py

Runs the PubmedID caching system (requires web.py)
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
from Bio import (Entrez, Medline)

urls=("/(\d+)", "PubmedRecord")
app = web.application(urls, globals())
DEFAULT_CACHE_NAME=os.path.join(cache.path(), "pubmed_cache.db")
DEFAULT_CACHE_PORT=8081
DEFAULT_CACHE_HOST="http://127.0.0.1:%d" % DEFAULT_CACHE_PORT

# Replace your email address below!
Entrez.email="Jorge.R.Herskovic@uth.tmc.edu"

class PubmedRecord(object):
    """Serves PubMed records via a RESTful API"""
    def __init__(self):
        try:
            self._cache_location=sys.argv[2]
        except IndexError:
            self._cache_location=DEFAULT_CACHE_NAME
        self._cache=StringDBDict(self._cache_location, file_mode="c")
        
    def GET(self, pubmed_id):
        web.header('Content-type', 'application/octet-stream')
        try:
            record=self._cache[int(pubmed_id)]
        except:
            record=None
            print >>sys.stderr, "Error when retrieving %r. Traceback follows." \
                    % pubmed_id
            print >>sys.stderr, traceback.format_exc()
        return pickle.dumps(record, pickle.HIGHEST_PROTOCOL)
    
    def POST(self, pubmed_id):
        record=web.input().record
        record=pickle.loads(str(record))
        self._cache[int(pubmed_id)]=record
        return
        
class Client(object):
    """Meant to be imported from other modules to interact with the server."""
    def __init__(self, server_url):
        self._my_server_url=server_url
    def get_record(self, record_num):
        url="%s/%d" % (self._my_server_url, record_num)
        try:
            record=urllib2.urlopen(url).read()
        except urllib2.HTTPError:
            return None
        try:
            record=pickle.loads(record)
        except IOError:
            record=None
        return record
    def put_record(self, record_num, data):
        url="%s/%d" % (self._my_server_url, record_num)
        url_data=urlencode({"record": pickle.dumps(data)})
        try:
            urllib2.urlopen(url, url_data)
        except urllib2.HTTPError:
            return False
        return True
    def fetch_record(self, record_num):
        """Retrieves a record from MEDLINE"""
        handle=Entrez.efetch(db="pubmed", id=[record_num], 
                             rettype="medline", retmode="text")
        my_record=Medline.parse(handle).next()
        return my_record
        
if __name__ == '__main__':
    app.run()

