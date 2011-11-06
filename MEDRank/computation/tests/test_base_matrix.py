#!/usr/bin/env python
# encoding: utf-8
"""
test_base_matrix.py

Created by Jorge Herskovic on 2010-06-09.
Copyright (c) 2010 UTHSC School of Health Information Sciences. All rights reserved.
"""

import unittest
import numpy
from MEDRank.computation.base_matrix import Matrix

class test_base_matrix(unittest.TestCase):
    """The default matrix is a 5x5 matrix with the following setup:
    |  1.0  0.0  1.0 -1.0  2.5 |
    |  0.0  3.1  0.1  0.0 -7.9 |
    | -9.8  1.1  6.7  2.2 -4.0 |
    | 19.3  1.1  1.1  4.5 -9.9 |
    |  2.7  0.1  0.1 -3.0  1.0 |"""
    def setUp(self):
        self.m=Matrix(numpy.zeros([5, 5]))
        # Pull the matrix out of the docstring for the class. I'm lazy.
        rows=[x.strip() for x in self.__doc__.split('\n')]
        rows=[x for x in rows if x[0]=='|']
        rows=[[float(x) for x in y.strip('|').split()] for y in rows]
        for i in xrange(len(rows)):
            self.m[i]=rows[i]
    def testConstruction(self):
        self.assert_(isinstance(self.m, Matrix))
        self.assertEquals(self.m[1, 1], 3.1)
        self.assertEquals(self.m[4, 1], 0.1)
        self.assertEquals(self.m[3, 0], 19.3)
        self.assertEquals(self.m[4, 3], -3.0)
    def testIndexError(self):
        self.assertRaises(IndexError, self.m.__getitem__, (7, 8))
    def testRowSum(self):
        self.assertAlmostEquals(self.m.rowsum(0), 3.5)
        self.assertAlmostEquals(self.m.rowsum(2), -3.8)
    def testColSum(self):
        self.assertAlmostEquals(self.m.colsum(3), 2.7)
    def testMax(self):
        self.assertAlmostEquals(self.m.max(), 19.3)
    def testSize(self):
        self.assertEquals(len(self.m), 5)
    def testRowNonZero(self):
        self.assertEquals(self.m.row_nonzero(2), 5)
        self.assertEquals(self.m.row_nonzero(1), 3)
    def testColNonZero(self):
        self.assertEquals(self.m.col_nonzero(0), 4)
        self.assertEquals(self.m.row_nonzero(4), 5)
    def testTranspose(self):
        t=self.m.T
        for j in xrange(len(self.m)):
            for i in xrange(len(self.m)):
                self.assertEquals(self.m[i, j], t[j, i])
    def testEquals(self):
        t=self.m.transpose()
        tt=t.T
        self.assertEquals((self.m==tt).all(), True)
    def testNormalize(self):
        norm=self.m.normalize()
        self.assertAlmostEquals(norm[3, 0], 1.0)
        self.assertAlmostEquals(norm[3, 2], 0.05699481865285)

if __name__ == '__main__':
    unittest.main()