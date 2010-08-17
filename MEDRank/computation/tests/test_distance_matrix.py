#!/usr/bin/env python
# encoding: utf-8
"""
test_distance_matrix.py

Created by Jorge Herskovic on 2008-06-19.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import unittest
import sys
sys.path.append('../')
from distance_matrix import *
from MEDRank.computation.link_matrix import LinkMatrix

class test_distance_matrix(unittest.TestCase):
    def setUp(self):
        "Copied from test_link_matrix"
        self.my_matrix=LinkMatrix(5) # Create a 5x5 link_matrix
        """Creates the following links:
            0    1--->2--->3    4
            │                   ↻
            └──────────────────↗"""
        self.my_matrix[1, 2]=3
        self.my_matrix[4, 4]=4
        self.my_matrix[0, 4]=1
        self.my_matrix[2, 3]=2
    def testDistances(self):
        # The distances should be:
        # 0->4: 1
        # 1->2: 1
        # 2->3: 1
        # 1->3: 2
        # all others, 5 (the number of nodes)
        dist=DistanceMatrix(self.my_matrix)
        self.assertEqual(dist[1,2], 1)
        self.assertEqual(dist[0,4], 1)
        self.assertEqual(dist[1,4], 5)
        self.assertEqual(dist[4,4], 0)
        self.assertEqual(dist[1,3], 2)
    def testAltUnreachableDistance(self):
        dist=DistanceMatrix(self.my_matrix, -1)
        self.assertEqual(dist[1,2], 1)
        self.assertEqual(dist[0,4], 1)
        self.assertEqual(dist[1,4], -1)
        self.assertEqual(dist[4,4], 0)
        self.assertEqual(dist[1,3], 2)
    def testOutDistance(self):
        """The out distance of 1 should be: 5+0+1+2+5 (the sum of all its
        distances)"""
        dist=DistanceMatrix(self.my_matrix)
        self.assertEqual(13, dist.out_distance(1))
    def testInDistance(self):
        """The in distance of 4 should be: 1+5+5+5+0"""
        dist=DistanceMatrix(self.my_matrix)
        self.assertEqual(16, dist.in_distance(4))
    def testRelativeOutCentrality(self):
        """The converted distance for the matrix should be (according to the
        out distances):
        0: 0+5+5+5+1=16
        1: 5+0+1+2+5=13
        2: 5+5+0+1+5=16
        3: 5+5+5+0+5=20
        4: 5+5+5+5+0=20
        so the total should be 16+13+16+20+20=85
        Which means that 2's relative out centrality would be 85/16=5.3125"""
        dist=DistanceMatrix(self.my_matrix)
        self.assertEqual(5.3125, dist.relative_out_centrality(2))
    def testRelativeInCentrality(self):
        dist=DistanceMatrix(self.my_matrix)
        self.assertEqual(5.3125, dist.relative_in_centrality(4))
    def testCompactness(self):
        dist=DistanceMatrix(self.my_matrix)
        #Compactness is (max-converted_distance)/(max-min)
        the_max=(5**2-5)*5.0
        the_min=5**2-5.0
        converted_distance=85.0
        self.assertEqual((the_max-converted_distance)/(the_max-the_min),
                         dist.compactness())
    def testStratum(self):
        dist=DistanceMatrix(self.my_matrix)
        # The LAP for the matrix should be:
        # With an uneven N of 5, (5**3-5)/4=30
        # 0: 0+0+0+0+1=1
        # 1: 0+0+1+2+0=3
        # 2: 0+0+0+1+0=1
        # 3: 0+0+0+0+0=0
        # 4: 0+0+0+0+0=0
        # LAP=5 then. Status and contrastatus for each node:
        # For 0: status=1, contrastatus=0. abs=1
        # For 1: status=3, contrastatus=0. abs=3
        # For 2: status=1, contrastatus=1. abs=0
        # For 3: status=0, contrastatus=3. abs=3
        # For 4: status=0, contrastatus=1. abs=1
        # Σabs(status-contrastatus)=8
        # stratum=8/30=0.2666666667
        self.assertEqual(8.0/30.0, dist.stratum())
        
if __name__ == '__main__':
    unittest.main()