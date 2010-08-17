#!/usr/bin/env python
# encoding: utf-8
"""
test_savcc_normalized_matrix.py

Created by Jorge Herskovic on 2008-05-29.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import unittest
import sys
sys.path.append('../')
from savcc_normalized_matrix import *

# pylint: disable-msg=C0103,C0111,R0904        
class savcc_normalized_matrixTests(unittest.TestCase):
    def setUp(self):
        import math
        from test_savcc_matrix import create_fake_matrix
        #logging.getLogger().setLevel(logging.DEBUG)
        self.eval_func=lambda x: 1.0/math.exp(x) if x>=0 and x<5 else 0.0
        self.matrix=SavccNormalizedMatrix(create_fake_matrix(),
                                          self.eval_func)
    def testEvalFunction(self):
        self.assertEqual(self.eval_func(0), 1.0)
        self.assertEqual(self.eval_func(5), 0.0)
        self.assertAlmostEqual(self.eval_func(1), 0.3679, 3)
    def testGetItem(self):
        # Distance to itself = 1 with this eval function
        # So with the normalization factors it gets more complicated
        # These values should be OK
        self.assertAlmostEqual(self.matrix[1, 1], 0.2594964, 6)
        self.assertAlmostEqual(self.matrix[0, 1], 0.4223187, 6)
        self.assertAlmostEqual(self.matrix[1, 2], 0.0351190, 6)

if __name__ == '__main__':
    unittest.main()