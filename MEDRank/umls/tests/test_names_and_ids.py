#!/usr/bin/env python
# encoding: utf-8
"""
test_names_and_ids.py

Created by Jorge Herskovic on 2008-05-29.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import unittest
from MEDRank.umls.names_and_ids import *

class names_and_idsTests(unittest.TestCase):
    def setUp(self):
        self.nid=NamesAndIDs(['descriptor', 'qualifier', 'other'],
                               ['did', 'qid', 'nid'])
    def testQualifiers(self):
        self.assertEquals([x for x in self.nid.iter_qualifiers()], ['qid'])
    def testDescriptors(self):
        self.assertEquals([x for x in self.nid.iter_descriptors()], ['did'])
    def testCreationTest(self):
        raised=False
        try:
            nid2=NamesAndIDs(['one name'], 
                               ['descriptor one', 'descriptor two'])
        except ValueError:
            raised=True
        self.assert_(raised)


if __name__ == '__main__':
    unittest.main()