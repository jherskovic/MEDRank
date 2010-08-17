#!/usr/bin/env python
# encoding: utf-8
"""
test_common.py

Created by Jorge Herskovic on 2008-05-29.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import unittest
from MEDRank.evaluation.common import *

# pylint: disable-msg=C0103,C0111,R0904        
class commonTests(unittest.TestCase):
    def setUp(self):
        from MEDRank.evaluation.evaluation import EvaluationParameters
        self.params=EvaluationParameters()
    def testQuick(self):
        quickset=quick(self.params)
        # Since we can't assert test identity directly, we'll check that
        # there's one of each type instead
        self.assert_(Hoopers in [type(x) for x in quickset])
        self.assert_(Precision in [type(x) for x in quickset])
        self.assert_(Recall in [type(x) for x in quickset])
        self.assert_(GoldStandardCount in [type(x) for x in quickset])
        self.assert_(SeenCount in [type(x) for x in quickset])
        self.assert_(F2 in [type(x) for x in quickset])
        # and that there's five of them.
        self.assertEqual(6, len(quickset))
    def testComprehensive(self):
        self.params.mesh_tree=None
        self.params.savcc_matrix=None
        self.params.alpha=1.0
        comprehensiveset=comprehensive(self.params)
        # Since we can't assert test identity directly, we'll check that
        # there's one of each type instead
        self.assert_(Hoopers in [type(x) for x in comprehensiveset])
        self.assert_(Precision in [type(x) for x in comprehensiveset])
        self.assert_(Recall in [type(x) for x in comprehensiveset])
        self.assert_(Savcc in [type(x) for x in comprehensiveset])
        # and that there's four of them.
        self.assertEqual(7, len(comprehensiveset))
        
if __name__ == '__main__':
    unittest.main()