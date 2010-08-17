#!/usr/bin/env python
# encoding: utf-8
"""
test_precision.py

Created by Jorge Herskovic on 2008-05-29.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import unittest
from MEDRank.evaluation.precision import *

# pylint: disable-msg=C0103,C0111,R0904        
class precisionTests(unittest.TestCase):
    def setUp(self):
        self.e=Precision()
    def test_recall_and_precision(self):
        gold_standard=['a', 'b', 'c', 'd']
        self.assertEqual(self.e.evaluate([], ['a']), PrecisionResult(0.0))
        self.assertEqual(self.e.evaluate(gold_standard, ['a']), 
                         PrecisionResult(1.0))
        self.assertEqual(self.e.evaluate(gold_standard, ['a', 'b', 'z',
                                                         't']), 
                         PrecisionResult(0.5))

if __name__ == '__main__':
    unittest.main()