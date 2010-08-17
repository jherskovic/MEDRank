#!/usr/bin/env python
# encoding: utf-8
"""
test_bidirectional_search.py

Created by Jorge Herskovic on 2008-06-19.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import sys
import unittest
from MEDRank.computation.link_matrix import LinkMatrix
sys.path.append('../')
from bidirectional_search import search

class TestBiDiSearch(unittest.TestCase):
    def setUp(self):
        """The basic test's link structure will be a matrix describing 5 
        nodes with the following links between them:
            (0)-->(1)-->(2)-->(3)<--(4)
             ↑            ╲__ ↗|
             └─────────────────┘
        Same one used for every other test....
        """
        self.m=LinkMatrix(5) # Create a 5x5 link_matrix
        self.m[0, 1]=1
        self.m[1, 2]=1
        self.m[2, 3]=2
        self.m[4, 3]=1
        self.m[3, 0]=1
    def testSearch(self):
        # Try to find a path from 4 to 1
        self.assertEqual(search(self.m, self.m.transpose(), 4, 1), 
                         [4, 3, 0, 1])
        # 2->1
        self.assertEqual(search(self.m, self.m.transpose(), 2, 1),
                         [2, 3, 0, 1])
    def testEmptySearch(self):
        # 0->4 should be empty
        self.assertEqual(search(self.m, self.m.transpose(), 0, 4), [])

if __name__ == '__main__':
    unittest.main()