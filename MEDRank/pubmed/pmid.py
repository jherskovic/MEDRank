#!/usr/bin/env python
# encoding: utf-8
"""
pmid.py

Holds classes and functions to represent and handle PubMed IDs. Also retrieves
actual article records from PubMed if requested.

Created by Jorge Herskovic on 2008-05-13.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""
import re
from Bio import (Entrez, Medline)
import cPickle as pickle
import traceback
import os.path
import threading
import atexit
import Queue
from MEDRank.file.disk_backed_dict import StringDBDict, DatabaseError
from MEDRank.utility.logger import logging, ULTRADEBUG
from MEDRank.utility import cache
from MEDRank.utility import proctitle
import sys
try:
    from multiprocessing.managers import BaseManager
    multiprocessing_available=True
except ImportError:
    multiprocessing_available=False

Entrez.email="Jorge.R.Herskovic@uth.tmc.edu"

DEFAULT_CACHE_NAME=os.path.join(cache.path(), "pubmed_cache.db")

def PMIDCacheHandler(in_queue, out_queue, database_filename):
    """PMIDCacheHandler is supposed to run in its own thread and be called in
    a serialized fashion (i.e. please surround calls to this thing with locks!)
    It will process database requests serially. The main reason to do this is 
    that sqlite3 goes completely insane in a multithreaded environment, locking
    the DB for no good reason and refusing writes.
    
    The structure is that there's a manager process that controls access to the 
    DB thread. This manager process runs inside a multiprocessing.BaseManager 
    subclass, and synchronizes access to the DB. This way all processes will 
    access the underlying DB in a multi-process-friendly, synchronous fashion."""
    cache=StringDBDict(database_filename, file_mode="c")
    while True:
        request=in_queue.get()
        logging.debug("Processing request %s", request)
        if request=='STOP':
            break
        if request[0]=='GET':
            try:
                record=cache[request[1]]
            except:
                logging.debug("Exception when retrieving record %s: %s",
                             request[1], traceback.format_exc())
                record=None
                sys.exc_clear()
            out_queue.put(record)
        else:
            try:
                cache[request[1]]=request[2]
                result=True
            except:
                result=False
                logging.debug("Exception when storing record %s: %s",
                             request[1], traceback.format_exc())
                sys.exc_clear()
            out_queue.put(result)
    return
    
class PMIDCache(object):
    def __init__(self, database_name):
        self._req_queue=Queue.Queue()
        self._result_queue=Queue.Queue()
        self._work_thread=threading.Thread(target=PMIDCacheHandler, 
                                           args=(self._req_queue,
                                                 self._result_queue,
                                                 database_name))
        self._serializer=threading.Lock()
        self._pubmed_serializer=threading.Lock()
        self._work_thread.start()
        proctitle.setproctitle('MEDRank-Pubmed-cache')
    def __del__(self):
        self._req_queue.put('STOP')
    def get_record(self, pmid):
        pmid=str(pmid)
        self._serializer.acquire()
        logging.debug("Grabbed serializer for GET, thread %r", 
                      threading.currentThread())
        try:
            self._req_queue.put(('GET', pmid))
            record=self._result_queue.get()
            logging.debug("Received %r", record)
        finally:
            self._serializer.release()
            logging.debug("Released serializer for GET, thread %r", 
                          threading.currentThread())
        return record
    def put_record(self, pmid, record):
        pmid=str(pmid)
        logging.debug("Storing record %r", pmid)
        self._serializer.acquire()
        logging.debug("Grabbed serializer for PUT, thread %r", 
                      threading.currentThread())
        try:
            try:
                self._req_queue.put(('PUT', pmid, record))
                result=self._result_queue.get()
            except:
                logging.debug("Exception raised while storing record %s: %s",
                              pmid, traceback.format_exc())
                result=False
        finally:
            self._serializer.release()
            logging.debug("Released serializer for GET, thread %r", 
                          threading.currentThread())
        logging.debug("Record stored with result %r", result)
        return result
    def fetch_record(self, pmid):
        self._pubmed_serializer.acquire()
        #self._serializer.acquire()
        try:
            handle=Entrez.efetch(db="pubmed", id=[pmid], 
                             rettype="medline", retmode="text")
            my_record=Medline.parse(handle).next()
            # There's only one returned record, so we'll skip the generator crap
        finally:
            self._pubmed_serializer.release()
            #self._serializer.release()
        logging.debug("Got %r from the NLM", my_record)
        return my_record
        
if multiprocessing_available:        
    class PMIDManager(BaseManager):
        pass
    PMIDManager.register('PMIDCache', PMIDCache)

class Pmid(object):
    """A PubMed ID is a number that represents an article in PubMed 
    univocally."""
    __slots__=['__pmid']
    #__article_cache=None
    __article_cache_manager=None
    __article_cache=None
    __fetch_new=True
#    __article_cache_owner=None
    def __init__(self, a_pubmed_id=None):
        if a_pubmed_id is not None:
            self.__pmid=int(a_pubmed_id)
        else:
            self.__pmid=None
    @staticmethod
    def init_storage(cache_name=DEFAULT_CACHE_NAME, fetch_new_articles=True):
        if Pmid.__article_cache is None:
            if multiprocessing_available:
                Pmid.__article_cache_manager=PMIDManager()
                Pmid.__article_cache_manager.start()
            else:
                logging.debug("multiprocessing not available. "
                              "Setting up a dummy manager.")
                class dummyManager(object):
                    def PMIDCache(self, name):
                        return PMIDCache(name)
                        
                Pmid.__article_cache_manager=dummyManager()
            Pmid.__article_cache=\
                Pmid.__article_cache_manager.PMIDCache(cache_name)
            Pmid.__fetch_new=fetch_new_articles
        logging.log(ULTRADEBUG, 
                    "Started up a connection to the pubmed cache database.")  
    @staticmethod
    def close_storage():
        try:
            if Pmid.__article_cache is not None:
                del Pmid.__article_cache
        except AttributeError:
            pass
    def __repr__(self):
        return "<Pubmed ID %d @ %#x>" % (self.__pmid, id(self))
    def __str__(self):
        return str(self.__pmid)
    # The pmid property.
    def pmid_fget(self):
        return self.__pmid
    def pmid_fset(self, value):
        self.__pmid=int(value)
    pmid=property(pmid_fget, pmid_fset)
    def set_from_string(self, a_string, _regexp=re.compile(r'\d+')):
        """Sets the PubMed ID from a string, extracting the first integer it
        comes across. Raises ValueError if it can't find something like an
        integer."""
        try:
            self.pmid=_regexp.findall(a_string)[0]
        except IndexError:
            raise ValueError("There was no recognizable PubMed ID in %r" % 
                             a_string)
    def pubmed_url(self):
        """Returns a URL pointing to the PubMed entry for this article"""
        return """http://www.ncbi.nlm.nih.gov/pubmed/%d""" % self.__pmid
    def article_record(self):
        if Pmid.__article_cache is None:
            Pmid.init_storage()
        fetch=False
        my_record=self.__article_cache.get_record(self.__pmid)
        if my_record is not None:
            return my_record
        else:
            fetch=self.__fetch_new
            logging.warn('Could not read %s from the cache: \n',
                         self.__pmid)

        if fetch:
            my_record=self.__article_cache.fetch_record(self.__pmid)
            if not self.__article_cache.put_record(self.__pmid, my_record):
                logging.warn("Unable to update the database: \n%r",
                             my_record)
        else:
            raise KeyError("No record for article %r could be found." % self.__pmid)
        return my_record
    def __hash__(self):
        """Pmids can be used for collection keys, so they must be hashable. The
        obvious hash that complies with all the requirements for a well-behaved
        Python hash is the hash of the PubmedID number itself."""
        return hash(self.__pmid)
    def __eq__(self, other):
        """The only comparison that really makes sense between two PubMed IDs
        is equality, because the number only reflects the moment the article
        was added to the database."""
        try:
            otherpmid=other.__pmid
        except AttributeError:
            otherpmid=None
            # It's possible to be compared against None, and any PMID is not
            # equal to None
        return self.__pmid==otherpmid
    def __ne__(self, other):
        try:
            otherpmid=other.__pmid
        except AttributeError:
            otherpmid=None
            # It's possible to be compared against None, and any PMID is not
            # equal to None
        return self.__pmid!=otherpmid

def clean_storage():
    Pmid.close_storage()
    
atexit.register(clean_storage)
