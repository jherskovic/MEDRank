#!/usr/bin/env python
# encoding: utf-8
"""
f2.py

Created by Jorge Herskovic on 2008-12-02.
Copyright (c) 2008 University of Texas - Houston. All rights reserved.
"""

import unittest
from MEDRank.evaluation.f2 import *

class f2test(unittest.TestCase):
    def setUp(self):
        self.e=F2()
    def test_recall_and_precision(self):
        gold_standard=['a', 'b', 'c', 'd']
        self.assertEqual(self.e.evaluate([], ['a']), F2Result(0.0))
        self.assertAlmostEqual(self.e.evaluate(gold_standard, ['a']).result,
                         0.29412, 4)
        self.assertEqual(self.e.evaluate(gold_standard, ['a', 'b', 'z', 't']),
                         F2Result(0.5))


    
if __name__ == '__main__':
    unittest.main()