#!/usr/bin/env python
# encoding: utf-8
"""
pmid.py

Holds classes and functions to represent and handle PubMed IDs. Also retrieves
actual article records from PubMed if requested.

The separate Pubmed record server MUST be started before these objects are invoked.

Created by Jorge Herskovic on 2008-05-13.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""
import re
import atexit
from MEDRank.utility.logger import logging, ULTRADEBUG
from MEDRank.pubmed import pmid_cache

class Pmid(object):
    """A PubMed ID is a number that represents an article in PubMed 
    univocally."""
    __slots__=['__pmid']
    __article_cache=None
    __fetch_new=True
#    __article_cache_owner=None
    def __init__(self, a_pubmed_id=None):
        if a_pubmed_id is not None:
            self.__pmid=int(a_pubmed_id)
        else:
            self.__pmid=None
    @staticmethod
    def init_storage(cache_name=pmid_cache.DEFAULT_CACHE_HOST, 
                     fetch_new_articles=True):
        if Pmid.__article_cache is None:
            Pmid.__article_cache=pmid_cache.Client(cache_name)
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
