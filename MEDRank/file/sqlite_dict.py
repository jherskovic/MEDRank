#!/usr/bin/env python
# encoding: utf-8
"""
sqlite_dict.py

Implements a very basic dictionary on top of a SQLite3 database.
Since Python 2.6 doesn't implement shelve on sqlite3, I rolled my own.

Created by Jorge Herskovic on 2008-10-28.
Copyright (c) 2008 University of Texas - Houston. All rights reserved.
"""

import sqlite3
from sqlite3 import DatabaseError
import os.path
import os
import random
import time
import tempfile
import zlib
import cPickle as pickle
from UserDict import DictMixin
from MEDRank.utility.logger import logging, ULTRADEBUG

class SQLiteDict(DictMixin):
    """A SQLite database that emulates a dictionary. Base class for the DBDict 
    classes."""
    def __init__(self, persistent_file_name, isolation_level="IMMEDIATE", 
                 compression=False):
        self.my_persistence=persistent_file_name is not None
        if not self.my_persistence:
            # Not very elegant...
            self.my_filename=os.path.join(tempfile.gettempdir(),
                                          tempfile.gettempprefix() + 
                                          str(random.randint(0, 19283673)))
            logging.debug('No filename specified - using tempfile %s', 
                          self.my_filename)
        else:
            self.my_filename=os.path.abspath(persistent_file_name)
        self.__t=sqlite3.connect(self.my_filename, isolation_level=isolation_level)
        self.__t.text_factory=str
        self._commits_enabled=True # Only disable in very specific cases!
        self._create_table_if_necessary()
        self.compressed=compression
    def commits_fget(self):
        return self._commits_enabled
    def commits_fset(self, value):
        self._commits_enabled = value
        if value:
            self.__t.commit() # Commit immedately upon activation
    commits_enabled = property(commits_fget, commits_fset)
    def __getstate__(self):
        return {'f': self.my_filename,
                'p': self.my_persistence,
                'c': self._commits_enabled,
                'z': self.compressed}
    def __setstate__(self, state):
        self.my_filename=state['f']
        self.my_persistence=state['p']
        self._commits_enabled=state['c']
        try:
            self.compressed=state['z']
        except KeyError:
            self.compressed=False
        self.__t=sqlite3.connect(self.my_filename)
        self._create_table_if_necessary()
        self.__t.text_factory=str
    def _create_table_if_necessary(self):
        try:
            dummy=self.__t.execute('select * from s limit 1')
        except sqlite3.OperationalError:
            # Table doesn't exist
            logging.log(ULTRADEBUG, "Table doesn't exist - must be a new database.")
            self.__t.execute("""create table s 
                                (pkey TEXT PRIMARY KEY NOT NULL,
                                 data BLOB NOT NULL)""")
            logging.debug("Table created.")
        return
    def __del__(self):
        if self.my_persistence:
            self.__t.commit()
        self.__t.close()
        if not self.my_persistence:
            logging.log(ULTRADEBUG, "Deleting temporary file %r", self.my_filename)
            os.unlink(self.my_filename)
    def __contains__(self, key):
        try:
            row=self.__t.execute('SELECT pkey FROM s WHERE pkey=?', 
                                 [key])
        except DatabaseError:
            return False
        return row.fetchone() is not None
    def __repr__(self):
        return "<%s at %#x backed by %s>" % (self.__class__.__name__,
                                             id(self), self.my_filename)
    def __len__(self):
        length=int(self.__t.execute('SELECT count(pkey) FROM s')
                     .fetchone()[0])
        return length
    def __getitem__(self, key):
        data=self.__t.execute('SELECT data FROM s WHERE pkey=?',
                               [key]).fetchone()
        if data is None:
           raise KeyError('There is no element %r in the dictionary', key)
        try:
            if self.compressed:
                result=pickle.loads(zlib.decompress(str(data[0])))
            else:
                result=pickle.loads(str(data[0]))
        except EOFError:
            raise EOFError("Error while unpickling the value for key %r "
                           "(it was \"%s\")" % (key, data[0]))
        return result
    def __setitem__(self, key, value):
        if self.compressed:
            data=buffer(zlib.compress(pickle.dumps(value, pickle.HIGHEST_PROTOCOL), 9))
        else:
            data=buffer(pickle.dumps(value, pickle.HIGHEST_PROTOCOL))
                                        # errors
        self.__t.execute('INSERT OR REPLACE into s VALUES (?, ?)',
                             [key, data])
        if self._commits_enabled:
            self.__t.commit() # Needed for concurrency issues
    def __delitem__(self, key):
        if key not in self:
            raise KeyError('There is no element %r in the dictionary', key)
        self.__t.execute('DELETE FROM s WHERE pkey=?', [key])
        if self._commits_enabled:
            self.__t.commit()
    def __iter__(self):
        # This is necessary to avoid concurrency problems - but it may
        # result in weirdness if you're doing funny stuff with iterators!
        all_keys=[x[0] for x in self.__t.execute('SELECT pkey FROM s')]
        for k in all_keys:
            yield k
        return
    def iterkeys(self):
        """Iterates through the keys in the dictionary."""
        return self.__iter__()
    def keys(self):
        """The set of keys in the dictionary."""
        return [x for x in self.__iter__()]
    def itervalues(self):
        """Iterates through the values in the dictionary."""
        for d in self.__t.execute('SELECT data FROM s'):
            if self.compressed:
                yield pickle.loads(zlib.decompress(str(d[0])))
            else:
                yield pickle.loads(str(d[0]))
        return
    def iteritems(self):
        """Iterates through tuples, each being (key, value) for every key in
        the dictionary."""
        for k in self.__t.execute('SELECT pkey, data FROM s'):
            if self.compressed:
                yield k[0], pickle.loads(zlib.decompress(str(k[1])))
            else:
                yield k[0], pickle.loads(str(k[1]))
        return
    def close(self):
        pass
    def sync(self):
        self.__t.commit()

