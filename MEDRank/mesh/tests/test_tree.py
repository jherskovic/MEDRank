#!/usr/bin/env python
# encoding: utf-8
"""
test_tree.py

Created by Jorge Herskovic on 2008-05-29.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import unittest
from MEDRank.mesh.tree import *

# pylint: disable-msg=C0103,C0111,R0904        
class treeTests(unittest.TestCase):
    def setUp(self):
        # Set up a fake tree with three nodes
        self.my_tree=Tree(None, file_mode='c') # Creates an empty tree
        self.my_tree._tree['hairitis']=TreeNode('hairitis', 'MH', 'role',
                                              set(['A12.23.45']))
        self.my_tree._tree['hairiatic cancer']=TreeNode('hairiatic cancer',
                                                      'MH', 'role',
                                                      set(['A12.23.54.65',
                                                       'B01.23']))
        self.my_tree._tree['hareitosis']=TreeNode('hareitosis', 'SH', 'role',
                                                set(['B02.34']))
        self.my_tree.terms=self.my_tree._tree.keys()
        self.my_tree.num_terms=len(self.my_tree.terms)
        self.my_tree.terms.sort()
    def testCommonRoot(self):
        self.assertEqual(Tree.common_root('A12.23.45', 'A12.23.54'), 'A12.23')
        self.assertEqual(Tree.common_root('A12.23.45', 'A12.23'), 'A12.23')
        self.assertEqual(Tree.common_root('A12.23.45', 'A13.23'), '')
        self.assertEqual(Tree.common_root('', ''), '')
    def testSemanticDistance(self):
        self.assertEqual(self.my_tree.semantic_distance('hairitis',
                                                        'hareitosis'), 5)
        self.assertEqual(self.my_tree.semantic_distance('hairitis',
                                                        'hairiatic cancer'),
                                                        3)
    def testDistance(self):
        # No common path between these two
        self.assertEqual(self.my_tree.distance('hairitis', 'hareitosis'), -1)
        self.assertEqual(self.my_tree.distance('hairitis', 
                                               'hairiatic cancer'), 3)
        self.assertEqual(self.my_tree.distance('hairiatic cancer', 
                                               'hareitosis'), 4)
    def testTerms(self):
        self.assertEqual(['hairiatic cancer', 'hairitis', 'hareitosis'],
                         self.my_tree.terms)
    def testInvLookup(self):
        self.assertEqual(1, self.my_tree.index('hairitis'))
    def testVocabularyVectorGenerationOnEmptyList(self):
        v=self.my_tree.term_vector([])
        self.assertEqual(3, len(v))
        self.assertEqual(0.0, v.length())
    def testTermNotInTreeFailsVectorGeneration(self):
        # We're not doing this anymore
        #self.assertRaises(TermNotInTree, 
        #                  self.my_tree.term_vector, ['term not in tree'])
        pass
    def testVectorGeneratedCorrectly(self):
        v=self.my_tree.term_vector(['hareitosis'])
        self.assertEqual(1, v[2])
        self.assertEqual(0, v[0])
        self.assertEqual(0, v[1])
if __name__ == '__main__':
    unittest.main()