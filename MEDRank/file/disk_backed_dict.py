#!/usr/bin/env python
# encoding: utf-8
"""
disk_backed_dict.py

Modified to use SQLiteDict on Tuesday, October 28, 2008

Created by Jorge Herskovic on 2008-01-20.
Copyright (c) 2008 University of Texas - Houston. All rights reserved.
"""

from MEDRank.file.sqlite_dict import SQLiteDict, DatabaseError
import copy
import zlib
#import cPickle as pickle
#from multiprocessing.managers import BaseManager
#from multiprocessing import Manager
#from threading import RLock
from MEDRank.utility.logger import logging, ULTRADEBUG
import traceback
from UserDict import DictMixin
# pylint: disable-msg=C0103
KEYS_KEY='_@keys@_'
SYNC_KEY='_@sync_every@_'
COUNTER_KEY='_@write_counter@_'
WRITE_EVERY_KEY='_@write_every@_'
SPECIAL_KEYS=[KEYS_KEY, SYNC_KEY, COUNTER_KEY, WRITE_EVERY_KEY]

#class DataManager(BaseManager):
#    pass

#lock_manager=Manager()
#lock_manager.start()

# pylint: disable-msg=R0201
class StringDBDict(DictMixin):
    """Mimics a dictionary but stores arbitrary contents on disk through
    a DB file. The contents vanish when the program closes by default, but if
    the constructor receives a filename it will save state there when the 
    object is deleted, and restore from it when it gets the same filename
    back. Contents are serialized and unserialized through pickle.
    It REQUIRES the original keys to be strings.
    
    It has a NOP transform_key function that must be overridden by 
    descendants that want to use non-string keys. The function must
    unequivocally map keys to strings. 
    If there is a KEYS_KEY key in the datastore, it will be untouched but 
    unused by this class - it's up to descendents to use it for something.
    Descendents must override:
        transform_key
        __delitem__
        unfreeze
        freeze
        __iter__
    
    The reason to use a StringDBDict instead of something else is performance
    - it should be faster than a plain DBDict."""
    def __init__(self, persistent_file=None, sync_every_transactions=5,
                 write_out_every_transactions=100, file_mode="r", 
                 cachesize=1048576,
                 compression=False):
        logging.debug("Creating database for %r", persistent_file)
        self.my_store=SQLiteDict(persistent_file)
        logging.log(ULTRADEBUG, "Initializing internal state")
        self.my_mode=file_mode
        self.my_file=persistent_file
        self.my_store.compressed=compression
        self._sync_every=sync_every_transactions
        if self._sync_every==0:
            self.my_store.commits_enabled=False
        self.write_counter=0 
        self.write_every=write_out_every_transactions
        self.persistent=persistent_file is not None
        #self.my_lock=RLock()
        if self.persistent:
            self.unfreeze()
            self.integrity_checking()
    def sync_every():
        doc = "The sync_every property."
        def fget(self):
            return self._sync_every
        def fset(self, value):
            self._sync_every = value
            if value==0:
                self.my_store.commits_enabled=False
            else:
                self.my_store.commits_enabled=True
        def fdel(self):
            del self._sync_every
        return locals()
    sync_every = property(**sync_every())
    def transform_key(self, key, create_if_missing=False):
        """Transforms any key into the actual key used in the dictionary.
        Meant to be subclassed by any function that needs to use complex
        keys."""
        return key # Simplistic!
    def __contains__(self, key):
        return self.transform_key(key) in self.my_store
    def __repr__(self):
        return "<%s at %#x backed by %s>" % (self.__class__.__name__,
                                             id(self), self.my_file)
    def __del__(self):
        if self.persistent:
            #self.my_lock.acquire()
            self.freeze()
            self.my_store.close()
            #self.my_lock.release()
    def __len__(self):
        modifier=0
        for special_key in SPECIAL_KEYS:
            if special_key in self.my_store:
                modifier+=1
        return len(self.my_store)-modifier
    def __getitem__(self, key):
        result=self.my_store[self.transform_key(key)]
        return result
    def __setitem__(self, key, value):
        # Now supports setting the same thing twice!
        # This makes the key space discontiguous but it doesn't matter
        real_key=self.transform_key(key, True)
        #self.my_lock.acquire()
        try:
            self.my_store[real_key]=value
            self.write_counter+=1
            self.my_store[COUNTER_KEY]=str(self.write_counter) # Keep it updated
            if self._sync_every != 0 and \
                self.write_counter % self._sync_every == 0:
                self.my_store.sync()
            if self.write_every != 0 and \
                self.write_counter % self.write_every == 0:
                self.freeze()
        finally:
            #self.my_lock.release()
            pass
    def __delitem__(self, key):
        #self.my_lock.acquire()
        try:
            del self.my_store[self.transform_key(key)]
        finally:
            #self.my_lock.release()
            pass
    def __iter__(self):
        for k in self.my_store:
            if k in SPECIAL_KEYS:
                continue
            yield k
        return
    def integrity_checking(self):
        """Performs an integrity check on the database. Only useful for 
        derived classes."""
        logging.log(ULTRADEBUG, "NOP for a StringDBDict")
        return
    def iterkeys(self):
        """Iterates through the keys in the dictionary."""
        return self.__iter__()
    def keys(self):
        """The set of keys in the dictionary."""
        return [x for x in self.__iter__()]
    def itervalues(self):
        """Iterates through the values in the dictionary."""
        for k in self.__iter__():
            yield self.__getitem__(k)
        return
    def iteritems(self):
        """Iterates through tuples, each being (key, value) for every key in
        the dictionary."""
        for k in self.__iter__():
            yield k, self.__getitem__(k)
        return
    def freeze(self):
        """Dumps the configuration to special keys so that the DBDict
        state can be replicated later (i.e. for persistence).
        This procedure is performed every WRITE_EVERY writes, but
        COUNTER_KEY is kept updated continuously."""        
        if self.my_mode=="r":
            return
        #self.my_lock.acquire()
        try:
            self.my_store[SYNC_KEY]=str(self.sync_every)
            self.my_store[COUNTER_KEY]=str(self.write_counter)
            self.my_store[WRITE_EVERY_KEY]=str(self.write_every)
            self.my_store.sync()
        except:
            logging.warn("ERROR while storing state: %s", 
                         traceback.format_exc())
        #self.my_lock.release()
    def unfreeze(self):
        """Restores dictionary state from the database. Assumes a very 
        conservative state if it can't read state from disk."""
        # Is this the first-ever load??
        logging.log(ULTRADEBUG, "Restoring state from disk.")
        if len(self.my_store.keys())==0:
            return
        #self.my_lock.acquire()
        try:
            self.sync_every=int(self.my_store[SYNC_KEY])
        except KeyError:
            self.sync_every=1
        try:
            self.write_counter=int(self.my_store[COUNTER_KEY])
        except KeyError:
            self.write_counter=0
        try:
            # If there's no WRITE_EVERY, keep the default (for compatibility
            # With previous versions of the DBDict)
            result=int(self.my_store[WRITE_EVERY_KEY])
        except KeyError:
            result=self.write_every
        self.write_every=result
        #self.my_lock.release()
        logging.log(ULTRADEBUG, "State restored.")
        # Keep the values around in case of a crash
        #del self.my_store['_@keys@_']
        #del self.my_store['_@write_counter@_']
        #del self.my_store['_@sync_every@_']
        # self.my_store.sync()
    def clone(self):
        """Creates a second, temporary view of the dictionary that doesn't
        persist."""
        my_clone=copy.copy(self)
        # Clones shouldn't persist no matter what
        my_clone.persistent=False
        return my_clone    

class DBDict(StringDBDict):
    """Uses a second, hidden dictionary to keep track of the original keys.
    This way the keys can be anything."""
    def __init__(self, persistent_file=None, sync_every_transactions=5,
                 write_out_every_transactions=100, file_mode="r"):
        StringDBDict.__init__(self, persistent_file,    
                                  sync_every_transactions,
                                  write_out_every_transactions,
                                  file_mode=file_mode)
        if not self.persistent:
            self.original_keys={} # Created by Unfreeze, but unfreeze is
                                  # only called for persistent dictionaries
        self.reverse_key_mapping=None # Will only be created if requested
        #if self.persistent:
        #    self.unfreeze_keys()
    def transform_key(self, key, create_if_missing=False):
        """Stores keys in a secondary dictionary, autogenerating string keys
        if necessary for the database."""
        if create_if_missing:
            try:
                return self.original_keys[key]
            except KeyError:
                self.original_keys[key]=str(self.write_counter)
                return self.original_keys[key]
        else:
            return self.original_keys[key]
    def __delitem__(self, key):
        StringDBDict.__delitem__(self, key)
        del self.original_keys[key]
    def __iter__(self):
        for k in self.original_keys:
            yield k
        return
    def freeze(self):
        """Dumps the key dictionary to a special key so that the DBDict
        state can be replicated later (i.e. for persistence).
        This procedure is performed every sync_every writes, but
        COUNTER_KEY is kept updated continuously."""
        self.my_store[KEYS_KEY]=self.original_keys
        StringDBDict.freeze(self)
    def unfreeze(self):
        """Restores dictionary metastate from the database."""
        # Is this the first-ever load??
        if len(self.my_store.keys())==0:
            self.original_keys={}
        else:
            self.original_keys=self.my_store[KEYS_KEY]
        StringDBDict.unfreeze(self)
    def clone(self):
        """Creates a copy of the dictionary."""
        my_clone=copy.copy(self)
        my_clone.original_keys=copy.deepcopy(self.original_keys)
        # Clones shouldn't persist no matter what
        my_clone.persistent=False
        return my_clone
    def fake_delete(self, key):
        """Deletes an item from the keys without eliminating it from the
        underlying store. Very useful for the trainers."""
        del self.original_keys[key]

#DataManager.register('StringDBDict', StringDBDict)
#DataManager.register('DBDict', DBDict)
#data_manager=DataManager()
#data_manager.start()
#StringDBDict=data_manager.StringDBDict
#DBDict=data_manager.DBDict