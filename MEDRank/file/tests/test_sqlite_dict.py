#!/usr/bin/env python
# encoding: utf-8
"""
test_sqlite_dict.py

Created by Jorge Herskovic on 2008-05-29.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import unittest
from MEDRank.file.sqlite_dict import *

# pylint: disable-msg=C0103,C0111,R0904        
class DBDTests(unittest.TestCase):
    def setUp(self):
        self.my_dict=SQLiteDict(None)
        self.my_dict['puf']=1
        self.my_dict['2']={'a': 'b'}
        #self.my_dict.sync()
    def test_retrieval(self):
        self.assertEquals(self.my_dict['puf'], 1)
        self.assertEquals(self.my_dict['2'], {'a': 'b'})
    def test_iteration_keys(self):
        for k in self.my_dict:
            self.assert_(k in ['2', 'puf'])
    def test_iteration_values(self):
        for k in self.my_dict.itervalues():
            self.assert_(k in [1, {'a': 'b'}])
    def test_iteration_items(self):
        for k, v in self.my_dict.iteritems():
            self.assert_((k, v) in [('puf', 1), ('2', {'a': 'b'})])
    def test_deletion(self):
        del self.my_dict['2']
        self.assertEquals(self.my_dict['puf'], 1)
        self.assertRaises(KeyError, self.my_dict.__getitem__, '2')
    def test_update(self):
        self.assertEquals(self.my_dict['puf'], 1)
        self.my_dict['puf']=55
        self.assertEquals(self.my_dict['puf'], 55)
    def test_no_zero_bug(self):
        # Certain pickled strings are misinterpreted by sqlite, notably
        # the string for 0
        self.my_dict['blah']=0
        self.assertEquals(self.my_dict['blah'], 0)
        
if __name__ == '__main__':
    unittest.main()