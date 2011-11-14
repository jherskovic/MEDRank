#!/usr/bin/env python
# encoding: utf-8
"""
test_spreading_activation.py

Created by Jorge Herskovic on 2011-11-10.
Copyright (c) 2011 Jorge Herskovic. All rights reserved.
"""

import unittest
import sys
import numpy
from MEDRank.computation.spreading_activation import *
from MEDRank.computation.link_matrix import *

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
        self.m=LinkMatrix(numpy.zeros([5,5])) # Create a 5x5 link_matrix
        self.r=SpreadingActivation(epsilon=1e-30)
        self.r.max_iterations=3
        self.m[0, 1]=1
        self.m[1, 2]=1
        self.m[2, 3]=2
        self.m[4, 3]=1
        self.m[3, 0]=1
        self.e=[0.15] * len(self.m)
    def testEvaluation(self):
        pr=self.r.evaluate(self.m, self.e)
        self.assert_(pr[0]>pr[3])
        self.assert_(pr[0]>pr[1])
        self.assert_(pr[1]>pr[2])
        self.assert_(pr[3]>pr[2])
        self.assert_(pr[4]==min(pr))
    def testSingleLinkBetween2and3(self):
        """The results should be the same as with 2 links between 2 and 3"""
        self.m[2,3]=1
        pr=self.r.evaluate(self.m, self.e)
        self.assert_(pr[0]>pr[3])
        self.assert_(pr[0]>pr[1])
        self.assert_(pr[1]>pr[2])
        self.assert_(pr[3]>pr[2])
        self.assert_(pr[4]==min(pr))
        #print self.r.get_stats()
    def testStartingConditions(self):
        self.r._max_iter=-1 # No iterations will be attempted, can't use the regular setter
        pr=self.r.evaluate(self.m, self.e)
        self.assertEqual(pr, [1.0, 1.0, 1.0, 1.0, 1.0])
    def testSingleIteration(self):
        self.r.max_iterations=0
        pr=self.r.evaluate(self.m, self.e)
        self.assert_(pr[3]>pr[0])
        self.assertEqual(pr[0], pr[1])
        self.assertEqual(pr[1], pr[2])
        self.assert_(pr[3]>pr[2])
        self.assert_(pr[4]==min(pr))
    
if __name__ == '__main__':
    unittest.main()