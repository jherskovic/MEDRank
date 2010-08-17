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

# pylint: disable-msg=C0103,C0111,R0904
# Copied the LinkMatrix tests, as this class must pass them too
class mapped_link_matrixTests(unittest.TestCase):
    def setUp(self):
        self.my_matrix=MappedLinkMatrix(['term1',
                                         'term2',
                                         'term3',
                                         'term4',
                                         'term5']) # Create a 5x5 link_matrix
    def testDimensions(self):
        self.assertEquals(len(self.my_matrix), 5)
        self.assertRaises(IndexError, self.my_matrix.__getitem__, (5, 0))
        self.assertRaises(IndexError, self.my_matrix.__getitem__, (0, 5))
    def testInitializedWithZeros(self):
        for i in xrange(len(self.my_matrix)):
            for j in xrange(len(self.my_matrix)):
                self.assertEquals(self.my_matrix[i, j], 0.0)
    def fill_in_matrix(self):
        self.my_matrix[1, 2]=3
        self.my_matrix[4, 4]=4
        self.my_matrix[0, 4]=1
        self.my_matrix[2, 3]=2
    def testFilling(self):
        self.fill_in_matrix()
        self.assertEquals(self.my_matrix[1, 2], 3)
        self.assertEquals(self.my_matrix[4, 4], 4)
        self.assertEquals(self.my_matrix[0, 4], 1)
        self.assertEquals(self.my_matrix[2, 3], 2)
    def testNormalization(self):
        self.fill_in_matrix()
        norm=self.my_matrix.normalize()
        self.assertEquals(norm[1, 2], 0.75)
        self.assertEquals(norm[4, 4], 1)
        self.assertEquals(norm[0, 4], 0.25)
        self.assertEquals(norm[2, 3], 0.5)
    def testRowSum(self):
        self.fill_in_matrix()
        self.assertEquals(self.my_matrix.rowsum(0), 1)
        self.assertEquals(self.my_matrix.rowsum(1), 3)
        self.assertEquals(self.my_matrix.rowsum(2), 2)
        self.assertEquals(self.my_matrix.rowsum(3), 0)
        self.assertEquals(self.my_matrix.rowsum(4), 4)
    def testColSum(self):
        self.fill_in_matrix()
        self.assertEquals(self.my_matrix.colsum(0), 0)
        self.assertEquals(self.my_matrix.colsum(1), 0)
        self.assertEquals(self.my_matrix.colsum(2), 3)
        self.assertEquals(self.my_matrix.colsum(3), 2)
        self.assertEquals(self.my_matrix.colsum(4), 5)
    def testMax(self):
        self.fill_in_matrix()
        self.assertEquals(self.my_matrix.max(), 4)
        norm=self.my_matrix.normalize()
        self.assertEquals(norm.max(), 1)
    def testColNonZero(self):
        self.fill_in_matrix()
        self.assertEquals(self.my_matrix.col_nonzero(0), 0)
        self.assertEquals(self.my_matrix.col_nonzero(1), 0)
        self.assertEquals(self.my_matrix.col_nonzero(2), 1)
        self.assertEquals(self.my_matrix.col_nonzero(3), 1)
        self.assertEquals(self.my_matrix.col_nonzero(4), 2)
    def testRowNonZero(self):
        self.fill_in_matrix()
        self.assertEquals(self.my_matrix.row_nonzero(0), 1)
        self.assertEquals(self.my_matrix.row_nonzero(1), 1)
        self.assertEquals(self.my_matrix.row_nonzero(2), 1)
        self.assertEquals(self.my_matrix.row_nonzero(3), 0)
        self.assertEquals(self.my_matrix.row_nonzero(4), 1)
    def testNeighbors(self):
        self.fill_in_matrix()
        self.assertEquals(self.my_matrix.neighbors(0), [4])
        self.assertEquals(self.my_matrix.neighbors(1), [2])
        self.assertEquals(self.my_matrix.neighbors(2), [3])
        self.assertEquals(self.my_matrix.neighbors(3), [])
        self.assertEquals(self.my_matrix.neighbors(4), [4])
    def testAllNeighbors(self):
        self.fill_in_matrix()
        self.my_matrix[0, 2]=1
        self.assertEquals(self.my_matrix.all_neighbors(),
                          [[2, 4], [2], [3], [], [4]])
    def testTranspose(self):
        self.fill_in_matrix()
        t=self.my_matrix.transpose()
        self.assertEquals(t[2, 1], 3)
        self.assertEquals(t[4, 4], 4)
        self.assertEquals(t[4, 0], 1)
        self.assertEquals(t[3, 2], 2)
    def testTransposedNeighborhood(self):
        self.fill_in_matrix()    
        t=self.my_matrix.transpose()
        self.assertEquals(t.all_neighbors(), [[], [], [1], [2], [0, 4]])
    def testPosition(self):
        self.assertEqual(0, self.my_matrix.get_term_position('term1'))
        self.assertRaises(ValueError, self.my_matrix.get_term_position, 'hi')
    
if __name__ == '__main__':
    unittest.main()