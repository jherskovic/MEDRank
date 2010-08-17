#!/usr/bin/env python
# encoding: utf-8
"""
test_counts.py

Created by Jorge Herskovic on 2008-05-29.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import unittest
from MEDRank.evaluation.counts import *

class countsTests(unittest.TestCase):
    def setUp(self):
        self.goldstd=['term 1', 'term 2']
        self.seen=['term 1', 'term 2', 'term 3']
        self.empty=[]
    def testGoldStdCount(self):
        gstdc=GoldStandardCount().evaluate(self.goldstd, self.seen)
        self.assertEqual(GoldStandardCountResult(2), gstdc)
    def testSeenCount(self):
        sc=SeenCount().evaluate(self.goldstd, self.seen)
        self.assertEqual(SeenCountResult(3), sc)
    def testEmptyCount(self):
        ec=SeenCount().evaluate(self.goldstd, self.empty)
        self.assertEqual(SeenCountResult(0), ec)
if __name__ == '__main__':
    unittest.main()