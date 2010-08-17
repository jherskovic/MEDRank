#!/usr/bin/env python
# encoding: utf-8
"""
test_mapped_ranker.py

Created by Jorge Herskovic on 2008-05-29.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import sys
import unittest
sys.path.append('../')
from mapped_ranker import *

# pylint: disable-msg=C0103,C0111,R0904        
class mapped_rankerTests(unittest.TestCase):
    def setUp(self):
        """Copied from mapped_link_matrix and pageranker
            (0)-->(1)-->(2)-->(3)<--(4)
             ↑            ╲__ ↗|
             └─────────────────┘
        With this graph, node 3 should have the highest pagerank, followed by
        nodes 0, 1, 2 in that order. 4 should be the lowest.
        """
        self.m=MappedLinkMatrix(['term0',
                                 'term1',
                                 'term2',
                                 'term3',
                                 'term4']) # Create a 5x5 link_matrix

        self.r=MappedRanker(PageRanker(epsilon=1e-10))
        self.m[0, 1]=1
        self.m[1, 2]=1
        self.m[2, 3]=2
        self.m[4, 3]=1
        self.m[3, 0]=1
        self.e=[0.15] * len(self.m)
    def testMappedRankerCreatesRankerResultSets(self):
        ranking=self.r.evaluate(self.m, self.e)
        # print ranking
        self.assert_(type(ranking) is RankerResultSet)
    def testResultsMakeSense(self):
        ranking=self.r.evaluate(self.m, self.e)
        self.assert_(ranking['term3'] > ranking['term4'])
        self.assert_(ranking['term2'] < ranking['term0'])
    def testRankerAttributesAccessible(self):
        raised=False
        try:
            self.r.stats
        except:
            raised=True
        self.assertFalse(raised)

if __name__ == '__main__':
    unittest.main()