#!/usr/bin/env python
# encoding: utf-8
"""
test_evaluation.py

Created by Jorge Herskovic on 2008-05-29.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import unittest
from MEDRank.evaluation.evaluation import *

# pylint: disable-msg=C0103,C0111,R0904        
class evaluationTests(unittest.TestCase):
    def setUp(self):
        self.eval=Evaluation()
    def test_doesnt_work(self):
        self.assertEqual(Result(0.0), self.eval.evaluate([],[]))

if __name__ == '__main__':
    unittest.main()