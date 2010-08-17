#!/usr/bin/env python
# encoding: utf-8
"""
test_textranker.py

Created by Jorge Herskovic on 2008-05-29.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import unittest
from MEDRank.computation.textranker import *

# pylint: disable-msg=C0103,C0111,R0904        
class textrankerTests(unittest.TestCase):
    def setUp(self):
        """Fake matrix based on the PageRanker tests, but modified to resemble 
        adirectional links. The structure is thus:
        (0)<->(1)<->(2)<->(3)<->(4)
         ↑            ↖__ ↗↑
         └─────────────────┘
        """
        self.r=TextRanker(epsilon=1e-30) # Ensures that the iteration runs to
                                         # max_iter
        self.m=LinkMatrix(5) # Create a 5x5 link_matrix
        self.m[0, 1]=1; self.m[1, 0]=1
        self.m[1, 2]=1; self.m[2, 1]=1
        self.m[2, 3]=2; self.m[3, 2]=2
        self.m[4, 3]=1; self.m[3, 4]=1
        self.m[3, 0]=1; self.m[0, 3]=1
    def testOnEmptyMatrix(self):
        m=LinkMatrix(5)
        self.assertRaises(ZeroDivisionError, self.r.evaluate, m)
    def testRankingEmptyMatrix(self):
        empty_matrix=LinkMatrix(0)
        empty_e=[]
        self.assertRaises(ValueError, self.r.evaluate, empty_matrix)
    def testEvaluation(self):
        pr=self.r.evaluate(self.m)
        self.assert_(pr[3]>pr[0])
        self.assert_(pr[0]>pr[1])
        self.assert_(pr[2]>pr[1])
        self.assert_(pr[2]>pr[4])
        self.assert_(type(self.r.stats) is RankerStats)
        #print self.r.stats

if __name__ == '__main__':
    unittest.main()