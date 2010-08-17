#!/usr/bin/env python
# encoding: utf-8
"""
test_term.py

Created by Jorge Herskovic on 2008-05-29.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import unittest
from MEDRank.mesh.term import *

# pylint: disable-msg=C0103,C0111,R0904        
class termTests(unittest.TestCase):
    def setUp(self):
        self.my_term=Term('myocardial infarction', 'MeSH Heading')
    def testTerm(self):
        self.assertEqual(self.my_term.term, 'myocardial infarction')
    def testRole(self):
        self.assertEqual(self.my_term.role, 'mesh heading')
    def testEquality(self):
        other=Term('MyoCardIal infarction', 'another role')
        self.assertEqual(self.my_term, other)
        
if __name__ == '__main__':
    unittest.main()