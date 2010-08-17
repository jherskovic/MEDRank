#!/usr/bin/env python
# encoding: utf-8
"""
test_ranked_converter.py

Created by Jorge Herskovic on 2008-05-29.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import unittest
from MEDRank.umls.ranked_converter import *

# Tests copied from test_converter and modified
# pylint: disable-msg=C0103,C0111,R0904,W0212,W0612
from MEDRank.umls.concrete_concept import ConcreteConcept
from MEDRank.umls.concept import Concept
from MEDRank.mesh.tree import (Tree, TermNotInTree)
from MEDRank.mesh.term import Term
from MEDRank.mesh.tree_node import TreeNode
from MEDRank.umls.converter import (Converter, ConverterData, ConverterStats)
from MEDRank.computation.node import Node

class conversionTests(unittest.TestCase):
    def setUp(self):
        #logging.basicConfig(level=logging.DEBUG,
        #                    format='%(asctime)s %(levelname)s %(message)s')
        # Most of the functionality is really tested under test_converter
        self.my_tree=Tree(None, file_mode="c") # Creates an empty tree
        self.my_tree._tree['hairitis']=TreeNode('hairitis', 'MH', 
                                              set(['A12.23.45']))
        self.my_tree._tree['hairiatic cancer']=TreeNode('hairiatic cancer',
                                                      'MH',
                                                      set(['A12.23.54.65',
                                                       'B01.23']))
        self.my_tree._tree['hareitosis']=TreeNode('hareitosis', 'SH', 
                                                set(['B02.34']))
        self.empty_rules=ConverterData({},{},{},{}, {})
        self.ruleless_converter=RankedConverter(Converter(self.my_tree,
                                                self.empty_rules))
    def testStats(self):
        self.myStats=ConverterStats(['heuristics'])
        self.myStats['heuristics']=1
        self.assertEqual({'heuristics': 1}, self.myStats.stats)
    def buildConcepts(self):
        cc=ConcreteConcept('hareitosis', 'i', ['hareitosis'], ['B02.34'], 
                           [''])
        cc2=ConcreteConcept('inflammed hair cancer', 'a',
                            ['hairitis', 'hairiatic cancer'],
                            ['A12.23.45', 'B01.23'], [''])
        self.storage={'c12345': cc, 'c98765': cc2}
        Concept.init_storage(self.storage)
        return (Concept('c12345'), Concept('c98765'))
    def testConceptBuilding(self):
        c1, c2=self.buildConcepts()
        self.assert_(type(c1) is Concept)
        self.assert_(type(c2) is Concept)
        self.assertEqual(c1.CUI, 'c12345')
    def buildRankedResultSet(self):
        # A ranked result set has nodes and scores instead of concepts.
        c1, c2=self.buildConcepts()
        n1=Node(c1.CUI, c1.concept_name, 2)
        n2=Node(c2.CUI, c2.concept_name, 1)
        return [(n1, 2), (n2, 1)]
    def testBasicConversion(self):
        output=self.ruleless_converter.convert(self.buildRankedResultSet())
        self.assert_(type(output) is RankedConversionResult)
        output=[x for x in output]
        self.assertEqual(Term('hareitosis'), output[0][0].utterance[0])
    def testConversionPassesScoresOn(self):
        output=self.ruleless_converter.convert(self.buildRankedResultSet())
        self.assert_(type(output) is RankedConversionResult)
        output=[x[1] for x in output] # Get the scores
        self.assertEqual([2, 1], output)

if __name__ == '__main__':
    unittest.main()