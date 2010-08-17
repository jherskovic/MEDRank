#!/usr/bin/env python
# encoding: utf-8
"""
test_hoopers.py

Created by Jorge Herskovic on 2008-05-29.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import unittest
from MEDRank.evaluation.hoopers import *

# pylint: disable-msg=C0103,C0111,R0904        
class hoopersTests(unittest.TestCase):
    def setUp(self):
        self.e=Hoopers()
    def test_consistency(self):
        term_list_1=['a']
        term_list_2=['a']
        self.assertEqual(self.e.evaluate(term_list_1, term_list_2), 
                        HoopersResult(1.0))
        term_list_1.append('b')
        self.assertEqual(self.e.evaluate(term_list_1, term_list_2), 
                        HoopersResult(0.5))
        term_list_2.append('c')
        self.assertEquals(self.e.evaluate(term_list_1, term_list_2),
            HoopersResult(1.0/3))
        self.assertEqual(self.e.evaluate([], term_list_2), HoopersResult(0.0))
    def testResultColumnName(self):
        self.assertEqual(HoopersResult(0.0).column_name(), "HoopersResult")

if __name__ == '__main__':
    unittest.main()