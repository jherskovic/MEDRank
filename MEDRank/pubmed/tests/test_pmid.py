#!/usr/bin/env python
# encoding: utf-8
"""
tests.py

Created by Jorge Herskovic on 2008-05-29.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import unittest
from MEDRank.pubmed.pmid import *

# pylint: disable-msg=C0103,C0111,R0904
class pmidTests(unittest.TestCase):
    def setUp(self):
        self.a_pmid=Pmid()
    def test_setting(self):
        self.a_pmid.pmid=9876
        self.assertEquals(self.a_pmid.pmid, 9876)
    def test_setting_from_string_no_regexp(self):
        self.a_pmid.pmid='9876'
        self.assertEquals(self.a_pmid.pmid, 9876)
    def test_setting_regexp(self):
        self.a_pmid.set_from_string('12345')
        self.assertEquals(self.a_pmid.pmid, 12345)
        self.assertRaises(ValueError, self.a_pmid.set_from_string, 'blah')
        self.a_pmid.set_from_string('mi mama 1345')
        self.assertEquals(self.a_pmid.pmid, 1345)
        self.a_pmid.set_from_string('156789.txt')
        self.assertEquals(self.a_pmid.pmid, 156789)
        self.assertRaises(ValueError, self.a_pmid.set_from_string, '')
    def testEquality(self):
        self.a_pmid.set_from_string('12345')
        self.assertEquals(self.a_pmid, Pmid(12345))

if __name__ == '__main__':
    unittest.main()