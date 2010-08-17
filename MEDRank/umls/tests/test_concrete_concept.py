#!/usr/bin/env python
# encoding: utf-8
"""
test_concrete_concept.py

Created by Jorge Herskovic on 2008-05-29.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import unittest
from MEDRank.umls.concrete_concept import *

class concrete_conceptTests(unittest.TestCase):
    def setUp(self):
        self.cc=ConcreteConcept('Really concrete concept', 'I', 
                                 ['name1', 'name2', 'name3'],
                                 ['id1', 'id2', 'did3'],
                                 'smtp')
    def testNamesAndIDs(self):
        self.assertEquals(self.cc.names_and_ids, {'id1': 'name1', 
                                                  'id2': 'name2',
                                                  'did3': 'name3'})
    def testConceptName(self):
        self.assertEquals(self.cc.concept_name, 'Really concrete concept')
    def testMappingMethod(self):
        self.assertEquals(self.cc.mapping_method, 'I')
    def testDescriptors(self):
        self.assertEquals([x for x in
                           self.cc.names_and_ids.iter_descriptors()],
                           ['did3'])
    def testQualifiers(self):
        self.assertEquals([x for x in
                           self.cc.names_and_ids.iter_qualifiers()],
                           [])
        

if __name__ == '__main__':
    unittest.main()