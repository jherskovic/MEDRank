#!/usr/bin/env python
# encoding: utf-8
"""
concept.py

Implements a UMLS concept. 

Concepts should always be retrieved with the factory function getConcept(CUI)
if memory is a concern, but it'll probably be enough to simply instantiate
them, as they are in fact pretty lightweight.

concept.init_storage should be called with a storage object
(probably a StringDBDict) before the first invocation of anything
on the concept object itself.

Created by Jorge Herskovic on 2008-05-12.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""
# Disable warnings about spaces before operators (they drive me crazy)
# pylint: disable-msg=C0322

# Don't complain about my variable names, pylint
# pylint: disable-msg=C0103

# PyLint complains about Manager not having a Namespace member, which is false
# pylint: disable-msg=E1101
import sys
import os.path
import atexit
from MEDRank.utility.logger import logging, ULTRADEBUG
from MEDRank.file.disk_backed_dict import StringDBDict
try:
    from multiprocessing import Manager
    multiprocessing_available=True
except ImportError:
    multiprocessing_available=False


_DEFAULT_CONCEPT_STORAGE=os.path.join(sys.exec_prefix, "medrank_data",
                                      "umls_concepts.db")
_DEFAULT_CACHE_SIZE=10*(2**20) # 10 megabytes

# Concepts are implemented as Flyweight objects (see Design Patterns, p. 195)
# crossed with Proxy objects. The only data actually stored is the CUI, but 
# there's a lot of extra data in disk-backed databases. 
# The neat thing is that most concepts will be manipulated by MEDRank without
# accessing the extra data most of the time, so it will be reasonably 
# efficient.
# A concept is unequivocally identified by its CUI, so we create at most one
# object for each CUI. The underlying storage is a disk-backed dictionary, to
# which we provide attribute read-only access (i.e. any attribute we don't
# provide here gets requested from the underlying storage)
# This could've been a straight StringDBDict, I guess, but I wanted to give  
# concepts special recognition as first-class citizens.

class NoConceptInfoError(Exception):
    """Represents the lack of information about a concept."""
    pass

class Concept(object):
    """Represents a UMLS concept by its CUI."""
    __manager=None
    __storage=None
    __slots__=['__cui']
    def __init__(self, CUI):
        self.__cui=CUI
        if Concept.__storage is None:
            logging.info("Initializing concept storage from default location."
                         " If this isn't what you want, call "
                         "Concept.init_storage() before allocating a Concept")
            Concept.init_storage()
    def get_cui(self):
        "Getter for the CUI property"
        return self.__cui
    CUI=property(get_cui)
    @staticmethod
    def init_storage(storage=None, separate_process=False):
        "Starts the storage manager for concept information"
        if multiprocessing_available and separate_process:
            if Concept.__manager is None:
                logging.debug("Starting SyncManager to handle the Concept DB")
                Concept.__manager=Manager()
                logging.debug("Initializing shared namespace")
                Concept.__storage=Concept.__manager.Namespace()
                logging.debug("Namespace initialized")
        else:
            logging.debug("No multiprocessing - setting up a dummy manager")
            class dummyManager(object):
                pass
            Concept.__storage=dummyManager()
        # If there is indeed a storage in the multiprocessing 
        # namespace, use that.
        if storage is None:
            logging.log(ULTRADEBUG, "Attempting to pass the default"
                        " storage location as a StringDBDict to the"
                        " namespace Manager.")
            Concept.__storage.storage=\
                    StringDBDict(_DEFAULT_CONCEPT_STORAGE,
                                 cachesize=_DEFAULT_CACHE_SIZE)
        else:
            Concept.__storage.storage=storage
        logging.debug("Initialized Concept storage.")
    @staticmethod
    def close_storage():
        Concept.__storage.storage=None
    def __getattr__(self, name):
        try:
            return Concept.__storage.storage[self.__cui].__getattribute__(name)
        except KeyError:
            try:
                # Thanks to a bug in the original script, we have to try an
                # uppercase version too.
                return Concept.__storage.storage[self.__cui.upper()].__getattribute__(name)
            except KeyError:
                raise NoConceptInfoError("No info about %s in %r." % 
                                        (self.CUI, self.__storage))
    def __repr__(self):
        return "<%s: %r>" % (self.__class__.__name__, self.__cui)
    #def storage_fget(self):
    #    "Getter for the storage property"
    #    return Concept.__storage
    #storage = property(storage_fget)
    @staticmethod
    def get_all_names():
        "SLOW OPERATION - reads all of the concept names into a single list."
        if Concept.__storage is None:
            Concept.init_storage()
        return [x.concept_name 
                for x in Concept.__storage.storage.itervalues()]
    def __getstate__(self):
        return self.__cui
    def __setstate__(self, state):
        "Stores a CUI, and inits storage if necessary."
        self.__cui=state
        if Concept.__storage is None:
            Concept.init_storage()


#_my_concept_pool={}
#def getConcept(CUI):
#    """Retrieves a concept and keeps a cache of commonly-used concepts.
#    It will look in the cache first to avoid a database lookup if possible."""
#    try:
#        return _my_concept_pool[CUI]
#    except KeyError:
#        new_concept=Concept(CUI)
#        _my_concept_pool[CUI]=new_concept
#    return new_concept

# Caching disabled as it doesn't seem to make an iota of difference
def getConcept(CUI):
    return Concept(CUI)

def clean_storage():
    Concept.close_storage()

atexit.register(clean_storage)