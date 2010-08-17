#!/usr/bin/env python
# encoding: utf-8
"""
test_recall.py

Created by Jorge Herskovic on 2008-05-29.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import unittest
from MEDRank.evaluation.recall import *

# pylint: disable-msg=C0103,C0111,R0904        
class recallTests(unittest.TestCase):
    def setUp(self):
        self.e=Recall()
    def test_recall_and_precision(self):
        gold_standard=['a', 'b', 'c', 'd']
        self.assertEqual(self.e.evaluate([], ['a']), RecallResult(0.0))
        self.assertEqual(self.e.evaluate(gold_standard, ['a']), 
                         RecallResult(0.25))
        self.assertEqual(self.e.evaluate(gold_standard, ['a', 'b', 'z',
                                                         't']), 
                         RecallResult(0.5))


if __name__ == '__main__':
    unittest.main()