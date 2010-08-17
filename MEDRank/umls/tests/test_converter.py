#!/usr/bin/env python
# encoding: utf-8
"""
test_converter.py

Created by Jorge Herskovic on 2008-05-29.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import unittest
from MEDRank.umls.converter import *

# pylint: disable-msg=C0103,C0111,R0904,W0212,W0612
from MEDRank.umls.concrete_concept import ConcreteConcept
from MEDRank.umls.concept import Concept
from MEDRank.mesh.tree import (Tree, TermNotInTree)
from MEDRank.mesh.tree_node import TreeNode

class conversionTests(unittest.TestCase):
    def setUp(self):
        #logging.basicConfig(level=logging.DEBUG,
        #                    format='%(asctime)s %(levelname)s %(message)s')
        self.my_tree=Tree(None, file_mode="c") # Creates an empty tree
        self.my_tree._tree['hairitis']=TreeNode('hairitis', 'MH', 'Q',
                                              set(['A12.23.45']))
        self.my_tree._tree['hairiatic cancer']=TreeNode('hairiatic cancer',
                                                      'MH', 'Q',
                                                      set(['A12.23.54.65',
                                                       'B01.23']))
        self.my_tree._tree['hareitosis']=TreeNode('hareitosis', 'SH', 'Q',
                                                set(['B02.34']))
        self.empty_rules=ConverterData({},{},{},{}, {})
        self.ruleless_converter=Converter(self.my_tree, self.empty_rules)
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
    def testBasicConversion(self):
        c1, c2=self.buildConcepts()
        output=self.ruleless_converter.convert(c1)
        self.assertEqual(Term('hareitosis'), output.utterance[0])
    def testTypeAConversion(self):
        c1, c2=self.buildConcepts()
        output=self.ruleless_converter.convert(c2)
        self.assert_(Term('hairitis') in output.utterance)
        self.assert_(Term('hairiatic cancer') in output.utterance)
    def testExclusionList(self):
        c1, c2=self.buildConcepts()
        exclusion_list={'_exclusions': ['c98765']}
        convdata=ConverterData(exclusion_list, {}, {}, {}, {})
        excluding_converter=Converter(self.my_tree, convdata)
        self.assertEqual([Term('hareitosis')], 
                         excluding_converter.convert(c1).utterance)
        self.assertEqual([], 
                         excluding_converter.convert(c2).utterance)
    def testChecktagList(self):
        c1, c2=self.buildConcepts()
        new_list={'hair diseases': ['c12345']}
        # The rules are list->checktags to add
        checktag_rules={'hair diseases': ['hair']}
        convdata=ConverterData(new_list, checktag_rules, {}, {}, {})
        checktag_converter=Converter(self.my_tree, convdata)
        checktag_converter.start_conversion()
        converted_c1=checktag_converter.convert(c1)
        extra_output=checktag_converter.end_conversion()
        self.assertEqual([Term('hareitosis')], converted_c1.utterance)
        self.assertEqual([Term('hair')], extra_output.utterance)
        converted_c2=checktag_converter.convert(c2)
        self.assert_(Term('hairitis') in converted_c2.utterance)
        self.assert_(Term('hairiatic cancer') in converted_c2.utterance)
        self.assertEqual([], checktag_converter.end_conversion().utterance)
    def testSubheadingRules(self):
        c1, c2=self.buildConcepts()
        # One rule will add a subheading to c1, the other will exclude c2
        rules=[{'in': ['B02.34'], 'terms': ['styled']},
               {'in': ['B01.23'], 'not in': ['A12.23'], 'terms': ['not']}]
        # The rules are list->checktags to add
        convdata=ConverterData({}, {}, rules, {}, {})
        checktag_converter=Converter(self.my_tree, convdata)
        checktag_converter.start_conversion()
        converted_c1=checktag_converter.convert(c1)
        self.assert_(Term('styled') in converted_c1.utterance)
        self.assert_(Term('hareitosis') in converted_c1.utterance)
        self.assertEqual(2, len(converted_c1.utterance))
        converted_c2=checktag_converter.convert(c2)
        self.assert_(Term('hairitis') in converted_c2.utterance)
        self.assert_(Term('hairiatic cancer') in converted_c2.utterance)
        self.assertEqual(2, len(converted_c2.utterance))
        self.assertEqual([], checktag_converter.end_conversion().utterance)
    def testExtraChecktagList(self):
        # These should work like the subheading lists, but generate checktags
        # instead.
        c1, c2=self.buildConcepts()
        # One rule will add a subheading to c1, the other will exclude c2
        rules=[{'in': ['B02.34'], 'terms': ['styled']},
               {'in': ['B01.23'], 'not in': ['A12.23'], 'terms': ['not']}]
        convdata=ConverterData({}, {}, {}, rules, {})
        checktag_converter=Converter(self.my_tree, convdata)
        checktag_converter.start_conversion()
        converted_c1=checktag_converter.convert(c1)
        self.assert_(Term('hareitosis') in converted_c1.utterance)
        self.assertEqual(1, len(converted_c1.utterance))
        self.assertEqual([Term('styled')], 
                         checktag_converter.end_conversion().utterance)
        converted_c2=checktag_converter.convert(c2)
        self.assert_(Term('hairitis') in converted_c2.utterance)
        self.assert_(Term('hairiatic cancer') in converted_c2.utterance)
        self.assertEqual(2, len(converted_c2.utterance))
        self.assertEqual([], checktag_converter.end_conversion().utterance)
    def testWrongMappingType(self):
        c1, c2=self.buildConcepts()
        cc3=ConcreteConcept('hairosis', 'g/p', ['hairotic hairisis'], 
                           ['C1.2.3'], [''])
        # Add it in a roundabout way to the original storage
        self.storage['c2468']=cc3
        c3=Concept('c2468')
        self.assertEqual([], self.ruleless_converter.convert(c3).utterance)
    def testTermNotInTreeRaisesException(self):
        c1, c2=self.buildConcepts()
        cc3=ConcreteConcept('hairosis', 'i', 
                            ['hairotic hairisis',
                             'hair-raising hair', # <--This'll be a descriptor
                             'hurry'], 
                            ['Q12345678', 'D123456', 'Q987564'], [''])
        # Add it in a roundabout way to the original storage
        self.storage['c2468']=cc3
        c3=Concept('c2468')
        self.ruleless_converter._skip_unknown=False
        self.assertRaises(TermNotInTree,
                          self.ruleless_converter.convert, c3)
    def testDescriptorsPreferred(self):
        c1, c2=self.buildConcepts()
        cc3=ConcreteConcept('hairosis', 'i', 
                            ['hairotic hairisis',
                             'hair-raising hair', # <--This'll be a descriptor
                             'hurry'], 
                            ['Q12345678', 'D123456', 'Q987564'], [''])
        # Add it in a roundabout way to the original storage
        self.storage['c2468']=cc3
        c3=Concept('c2468')
        # Make sure the tree knows about this concept
        self.my_tree._tree['hair-raising hair']=TreeNode('hair-raising hair',
                                                         'MH', 'Q',
                                                         set(['B12.34']))
        self.assertEqual([Term('hair-raising hair')], 
                         self.ruleless_converter.convert(c3).utterance)
    def testDescriptorNamedLikeConceptPreferred(self):
        c1, c2=self.buildConcepts()
        cc3=ConcreteConcept('hair-raising hair', 'i', 
                            ['hairotic hairisis', # <-- a descriptor
                             'hair-raising hair', # <-- a descriptor
                             'hurry'], # <-- not a descriptor
                            ['D12345678', 'D123456', 'Q987564'],
                            [''])
        # Add it in a roundabout way to the original storage
        self.storage['c2468']=cc3
        c3=Concept('c2468')
        # Make sure the tree knows about this concept
        self.my_tree._tree['hair-raising hair']=TreeNode('hair-raising hair',
                                                         'MH', 'Q',
                                                         set(['B12.34']))
        self.assertEqual([Term('hair-raising hair')], 
                         self.ruleless_converter.convert(c3).utterance)
    def testDeepestOnePreferred(self):
        c1, c2=self.buildConcepts()
        cc3=ConcreteConcept('hair-raising hair', 'i', 
                            ['hairitis', # <-- a descriptor
                             'hairiatic cancer', # <-- a descriptor
                             'hareitosis'], # <-- a descriptor
                            ['D12345678', 'D123456', 'D987564'], [''])
        # Add it in a roundabout way to the original storage
        self.storage['c2468']=cc3
        c3=Concept('c2468')
        # Should choose the deepest one (hairiatic cancer, according to 
        # self.my_tree)
        self.assertEqual([Term('hairiatic cancer')],
                         self.ruleless_converter.convert(c3).utterance)
        
if __name__ == '__main__':
    unittest.main()