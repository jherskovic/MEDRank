#!/usr/bin/env python
# encoding: utf-8
"""
test_savcc_matrix.py

Created by Jorge Herskovic on 2008-05-29.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import unittest
import sys
import math
sys.path.append('../')
from savcc_matrix import *

def create_fake_matrix():
    """Creates a fake 3x3 matrix to use for tests. The matrix will have 1 in
    the main diagonal, and 0s elsewhere, except for 2,3 which will be equal to
    3."""
    import StringIO
    my_fake_matrix=''.join([struct.pack(">H", 3),
                            struct.pack(">H", 3),
                            struct.pack("<B", 1), # 1,1
                            struct.pack("<B", 0), # 1,2
                            struct.pack("<B", 0), # 1,3
                            struct.pack("<B", 0), # 2,1
                            struct.pack("<B", 1), # 2,2
                            struct.pack("<B", 3), # 2,3
                            struct.pack("<B", 0), # 3,1
                            struct.pack("<B", 0), # 3,2
                            struct.pack("<B", 1)]) # 3,3
    fake_file=StringIO.StringIO(my_fake_matrix)
    fake_file.fileno=lambda: 77 # Necessary for the testing call 
    fake_file.name="_fake_matrix_file"
    return fake_file

# pylint: disable-msg=C0103,C0111,R0904        
class savcc_matrixTests(unittest.TestCase):
    def setUp(self):
        self.eval_func=lambda x: 1.0/math.exp(x) if x>=0 and x<5 else 0.0
        #logging.getLogger().setLevel(logging.DEBUG)
        self.matrix=SavccMatrix(create_fake_matrix(),
                                self.eval_func)
    def testEvalFunction(self):
        self.assertEqual(self.eval_func(0), 1.0)
        self.assertEqual(self.eval_func(5), 0.0)
        self.assertAlmostEqual(self.eval_func(1), 0.3679, 3)
    def testGetItem(self):
        # Distance to itself = 1 with this eval function
        self.assertAlmostEqual(self.matrix[0, 0], 0.3679, 3)
        self.assertEqual(self.matrix[0, 1], 1.0)
        self.assertEqual(self.matrix[0, 2], 1.0)
        self.assertAlmostEqual(self.matrix[1, 1], 0.3678794, 5)
        self.assertEqual(self.matrix[1, 2], self.eval_func(3))
        self.assertAlmostEqual(self.matrix[2, 2], 0.3678794, 5)
    def testDimensionLimits(self):
        self.assertRaises(AssertionError, self.matrix.__getitem__, (-1, 0))
        self.assertRaises(AssertionError, self.matrix.__getitem__, (0, 9999998))
        self.assertRaises(AssertionError, self.matrix.__getitem__, (99999998, 0))
        self.assertRaises(AssertionError, self.matrix.__getitem__, (0, -5))
    def testMultiplication(self):
        v=VocabularyVector(3)
        r=self.matrix.mult_by_vector(v)
        self.assertEqual(r[0], 0.0)
        self.assertEqual(r[1], 0.0)
        self.assertEqual(r[2], 0.0)
        v[0]=1.0
        r=self.matrix.mult_by_vector(v)
        self.assertAlmostEqual(r[0], 0.3678794, 6)
        self.assertEqual(r[1], 1.0)
        self.assertEqual(r[2], 1.0)
    
if __name__ == '__main__':
    unittest.main()