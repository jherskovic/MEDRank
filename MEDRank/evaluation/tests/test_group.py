#!/usr/bin/env python
# encoding: utf-8
"""
test_group.py

Created by Jorge Herskovic on 2008-05-29.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import unittest
from MEDRank.evaluation.group import *

# pylint: disable-msg=C0103,C0111,R0904        
class groupTests(unittest.TestCase):
    def setUp(self):
        from MEDRank.evaluation.precision import Precision
        from MEDRank.evaluation.recall import Recall
        self.my_eval_set=EvaluationGroup([Precision(), Recall()])
        self.gold_standard=['a', 'b', 'c', 'd']
        self.test_string=['b', 'c', 'z']
    def testResults(self):
        from MEDRank.evaluation.precision import PrecisionResult
        from MEDRank.evaluation.recall import RecallResult
        results=self.my_eval_set.evaluate(self.gold_standard, 
                                          self.test_string)
        expected_results=ResultSet([PrecisionResult(2.0/3),
                                    RecallResult(0.5)])
        self.assertEqual(expected_results, results)
    def testEmptyEvaluator(self):
        emptyEvaluator=EvaluationGroup([])
        self.assertEqual(emptyEvaluator.evaluate(self.gold_standard,
                                                 self.test_string), 
                         ResultSet([]))
    
if __name__ == '__main__':
    unittest.main()