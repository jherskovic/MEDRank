#!/usr/bin/env python
# encoding: utf-8
"""
test_pageranker.py

Created by Jorge Herskovic on 2008-05-29.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import unittest
import sys
sys.path.append('../')
from pageranker import *

# pylint: disable-msg=C0103,C0111,R0904        
class rankerTests(unittest.TestCase):
    def setUp(self):
        """The basic test's link structure will be a matrix describing 5 
        nodes with the following links between them:
            (0)-->(1)-->(2)-->(3)<--(4)
             ↑            ╲__ ↗|
             └─────────────────┘
        With this graph, node 3 should have the highest pagerank, followed by
        nodes 0, 1, 2 in that order. 4 should be the lowest.
        """
        self.m=LinkMatrix(5) # Create a 5x5 link_matrix
        self.r=PageRanker(epsilon=1e-30)
        self.m[0, 1]=1
        self.m[1, 2]=1
        self.m[2, 3]=2
        self.m[4, 3]=1
        self.m[3, 0]=1
        self.e=[0.15] * len(self.m)
    def testEvaluation(self):
        pr=self.r.evaluate(self.m, self.e)
        self.assert_(pr[3]>pr[0])
        self.assert_(pr[0]>pr[1])
        self.assert_(pr[1]>pr[2])
        self.assert_(pr[2]>pr[4])
        #print self.r.stats
    def testOnEmptyMatrix(self):
        m=LinkMatrix(5)
        self.assertRaises(ZeroDivisionError, self.r.evaluate, 
                         m, [0, 0, 0, 0, 0])
    def testSingleLinkBetween2and3(self):
        """The results should be the same as with 2 links between 2 and 3"""
        self.m[2,3]=1
        pr=self.r.evaluate(self.m, self.e)
        self.assert_(pr[3]>pr[0])
        self.assert_(pr[0]>pr[1])
        self.assert_(pr[1]>pr[2])
        self.assert_(pr[2]>pr[4])
        #print self.r.get_stats()
    def testRankingEmptyMatrix(self):
        empty_matrix=LinkMatrix(0)
        empty_e=[]
        self.assertRaises(ValueError, self.r.evaluate, empty_matrix, empty_e)

if __name__ == '__main__':
    unittest.main()