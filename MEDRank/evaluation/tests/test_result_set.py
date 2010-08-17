#!/usr/bin/env python
# encoding: utf-8
"""
test_result_set.py

Created by Jorge Herskovic on 2008-05-29.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import unittest
from MEDRank.evaluation.result_set import *

class result_setTests(unittest.TestCase):
    def setUp(self):
        from MEDRank.evaluation.hoopers import HoopersResult
        from MEDRank.evaluation.precision import PrecisionResult
        self.my_tests=ResultSet([HoopersResult(0.0), PrecisionResult(1.0)])
    def testColumns(self):
        self.assertEquals(set(['HoopersResult', 'PrecisionResult']), 
                          self.my_tests.columns())
    def testDictOutput(self):
        self.assertEquals({'HoopersResult': 0.0, 'PrecisionResult': 1.0},
                           self.my_tests.as_dict())
if __name__ == '__main__':
    unittest.main()