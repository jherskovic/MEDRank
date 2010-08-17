#!/usr/bin/env python
# encoding: utf-8
"""
test_concept.py

Created by Jorge Herskovic on 2008-05-29.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import unittest
from MEDRank.umls.concept import *
#from MEDRank.umls.concept import _my_concept_pool # Import hidden variable
                                                  # explicitly
class my_concrete_concept(object):
    pass
    
class conceptTests(unittest.TestCase):
    def setUp(self):

        o=my_concrete_concept()
        o.name='a name'
        storage={'c1234': o}
        Concept.init_storage(storage)
    #def tearDown(self):
    #    global _my_concept_pool
    #    _my_concept_pool={}
    def testInstantiation(self):
        a=Concept('c1234')
        self.assertEquals(a.CUI, 'c1234')
    def testAttributeAccess(self):
        a=Concept('c1234')
        self.assertEquals(a.name, 'a name')
#    def testPool(self):
#        self.assertEquals(_my_concept_pool, {})
#        c=getConcept('c1234')
#        self.assertEquals(c.CUI, 'c1234')
#        d=getConcept('c1234')
#        self.assertEquals(id(c), id(d))
    def testInfoAboutConceptNotInStorageFails(self):
        e=getConcept('c9876')
        # You can create a concept with an unknown ID
        self.assert_(type(e) is Concept)
        # But you can't get info about it...
        self.assertRaises(NoConceptInfoError, e.__getattr__, 'test')
if __name__ == '__main__':
    unittest.main()