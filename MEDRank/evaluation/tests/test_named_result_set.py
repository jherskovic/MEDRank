#!/usr/bin/env python
# encoding: utf-8
"""
test_named_result_set.py

Created by Jorge Herskovic on 2009-03-26.
Copyright (c) 2009 University of Texas - Houston. All rights reserved.
"""

import unittest
import sys
sys.path.append('../')
from named_result_set import NamedResultSet
from result_set import ResultSet
from MEDRank.evaluation.hoopers import HoopersResult
from MEDRank.evaluation.precision import PrecisionResult

class test_named_result_set(unittest.TestCase):
    def setUp(self):
        self.my_tests=NamedResultSet('test_', [HoopersResult(0.0), PrecisionResult(1.0)])
    def testColumns(self):
        self.assertEquals(set(['test_HoopersResult', 'test_PrecisionResult']), 
                          self.my_tests.columns())
    def testDictOutput(self):
        self.assertEquals({'test_HoopersResult': 0.0, 'test_PrecisionResult': 1.0},
                           self.my_tests.as_dict())               
    def testColumnNamesOfResults(self):
        r=self.my_tests.pop()
        self.assert_(r.column_name() in
                     ["test_HoopersResult", "test_PrecisionResult"])
        r=self.my_tests.pop()
        self.assert_(r.column_name() in
                     ["test_HoopersResult", "test_PrecisionResult"])
    def testMixingWithRegularResultSet(self):
        another_result_set=ResultSet([HoopersResult(0.5)])
        # self.my_tests |= another_result_set
        self.assertEquals((self.my_tests | another_result_set).columns(),
                          set(['test_HoopersResult', 
                               'test_PrecisionResult',
                               'HoopersResult']))
        self.assertEquals((another_result_set | self.my_tests).columns(),
                          set(['test_HoopersResult', 
                               'test_PrecisionResult',
                               'HoopersResult']))
        
if __name__ == '__main__':
    unittest.main()