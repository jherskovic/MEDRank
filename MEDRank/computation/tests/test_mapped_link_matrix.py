#!/usr/bin/env python
# encoding: utf-8
"""
test_mapped_link_matrix.py

Created by Jorge Herskovic on 2008-05-29.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import sys
import unittest
from MEDRank.computation.mapped_link_matrix import *
import numpy

# pylint: disable-msg=C0103,C0111,R0904
# Copied the LinkMatrix tests, as this class must pass them too
class mapped_link_matrixTests(unittest.TestCase):
    def setUp(self):
        self.my_graph = MappedLinkMatrix(numpy.zeros([5, 5]))
        self.my_graph.terms = ['term1', 'term2', 'term3', 'term4', 'term5']
    def testDimensions(self):
        self.assertEquals(len(self.my_graph), 5)
        self.assertRaises(IndexError, self.my_graph.__getitem__, (5, 0))
        self.assertRaises(IndexError, self.my_graph.__getitem__, (0, 5))
    def testInitializedWithZeros(self):
        for i in xrange(len(self.my_graph)):
            for j in xrange(len(self.my_graph)):
                self.assertEquals(self.my_graph[i, j], 0.0)
    def fill_in_matrix(self):
        self.my_graph[1, 2] = 3
        self.my_graph[4, 4] = 4
        self.my_graph[0, 4] = 1
        self.my_graph[2, 3] = 2
    def testFilling(self):
        self.fill_in_matrix()
        self.assertEquals(self.my_graph[1, 2], 3)
        self.assertEquals(self.my_graph[4, 4], 4)
        self.assertEquals(self.my_graph[0, 4], 1)
        self.assertEquals(self.my_graph[2, 3], 2)
    def testNormalization(self):
        self.fill_in_matrix()
        norm = self.my_graph.normalize()
        self.assertEquals(norm[1, 2], 0.75)
        self.assertEquals(norm[4, 4], 1)
        self.assertEquals(norm[0, 4], 0.25)
        self.assertEquals(norm[2, 3], 0.5)
    def testRowSum(self):
        self.fill_in_matrix()
        self.assertEquals(self.my_graph.rowsum(0), 1)
        self.assertEquals(self.my_graph.rowsum(1), 3)
        self.assertEquals(self.my_graph.rowsum(2), 2)
        self.assertEquals(self.my_graph.rowsum(3), 0)
        self.assertEquals(self.my_graph.rowsum(4), 4)
    def testColSum(self):
        self.fill_in_matrix()
        self.assertEquals(self.my_graph.colsum(0), 0)
        self.assertEquals(self.my_graph.colsum(1), 0)
        self.assertEquals(self.my_graph.colsum(2), 3)
        self.assertEquals(self.my_graph.colsum(3), 2)
        self.assertEquals(self.my_graph.colsum(4), 5)
    def testMax(self):
        self.fill_in_matrix()
        self.assertEquals(self.my_graph.max(), 4)
        norm = self.my_graph.normalize()
        self.assertEquals(norm.max(), 1)
    def testColNonZero(self):
        self.fill_in_matrix()
        self.assertEquals(self.my_graph.col_nonzero(0), 0)
        self.assertEquals(self.my_graph.col_nonzero(1), 0)
        self.assertEquals(self.my_graph.col_nonzero(2), 1)
        self.assertEquals(self.my_graph.col_nonzero(3), 1)
        self.assertEquals(self.my_graph.col_nonzero(4), 2)
    def testRowNonZero(self):
        self.fill_in_matrix()
        self.assertEquals(self.my_graph.row_nonzero(0), 1)
        self.assertEquals(self.my_graph.row_nonzero(1), 1)
        self.assertEquals(self.my_graph.row_nonzero(2), 1)
        self.assertEquals(self.my_graph.row_nonzero(3), 0)
        self.assertEquals(self.my_graph.row_nonzero(4), 1)
    def testNeighbors(self):
        self.fill_in_matrix()
        self.assertEquals(self.my_graph.neighbors(0), [4])
        self.assertEquals(self.my_graph.neighbors(1), [2])
        self.assertEquals(self.my_graph.neighbors(2), [3])
        self.assertEquals(self.my_graph.neighbors(3), [])
        self.assertEquals(self.my_graph.neighbors(4), [4])
    def testAllNeighbors(self):
        self.fill_in_matrix()
        self.my_graph[0, 2] = 1
        self.assertEquals(self.my_graph.all_neighbors(),
                          [[2, 4], [2], [3], [], [4]])
    def testTranspose(self):
        self.fill_in_matrix()
        t = self.my_graph.transpose()
        self.assertEquals(t[2, 1], 3)
        self.assertEquals(t[4, 4], 4)
        self.assertEquals(t[4, 0], 1)
        self.assertEquals(t[3, 2], 2)
    def testTransposedNeighborhood(self):
        self.fill_in_matrix()    
        t = self.my_graph.transpose()
        self.assertEquals(t.all_neighbors(), [[], [], [1], [2], [0, 4]])
    def testPosition(self):
        self.assertEqual(0, self.my_graph.get_term_position('term1'))
        self.assertRaises(ValueError, self.my_graph.get_term_position, 'hi')
    
if __name__ == '__main__':
    unittest.main()
