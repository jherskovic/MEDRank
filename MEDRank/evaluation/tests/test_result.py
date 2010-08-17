#!/usr/bin/env python
# encoding: utf-8
"""
test_result.py

Created by Jorge Herskovic on 2008-05-29.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import unittest
from MEDRank.evaluation.result import *

# pylint: disable-msg=C0103,C0111,R0904
class resultTests(unittest.TestCase):
    def setUp(self):
        self.my_result=Result(1.0)
        self.another_result=Result(0.0)
    def testCreatedProperly(self):
        self.assert_(self.my_result is not None)
        self.assert_(self.another_result is not None)
    def testResultReading(self):
        self.assertEquals(1.0, self.my_result.result)
        self.assertEquals(0.0, self.another_result.result)
    def testResultSetting(self):
        raised=False
        try:
            self.my_result.result=-1
        except AttributeError:
            raised=True
        self.assert_(raised)
    def testInequality(self):
        self.assertNotEquals(self.my_result, self.another_result)
    def testEquality(self):
        self.assertEquals(self.my_result, Result(1.0))
    def testColumnName(self):
        self.assertEquals(self.my_result.column_name(), "Result")

if __name__ == '__main__':
    unittest.main()