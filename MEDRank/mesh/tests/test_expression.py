#!/usr/bin/env python
# encoding: utf-8
"""
test_expression.py

Created by Jorge Herskovic on 2008-05-29.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import unittest
from MEDRank.mesh.expression import *

# pylint: disable-msg=C0103,C0111,R0904        
class expressionTests(unittest.TestCase):
    def setUp(self):
        pass
    def testConstructionFromList(self):
        a_list=["First", "second", 'third']
        my_expr=Expression(a_list)
        self.assertEqual(my_expr.utterance, a_list)
    def testEmptyMajorHeadings(self):
        a_list=["First", "second", 'third']
        my_expr=Expression(a_list)
        self.assertEqual(my_expr.major_heading(), [])
    def testConstructionFromSingleItem(self):
        my_expr=Expression(1)
        self.assertEqual(my_expr.utterance, [1])
    def testListExpressionAdding(self):
        my_list=ExpressionList()
        my_list.append(Expression([Term('a')]))
        self.assertEqual([Expression([Term('a')])], my_list)
        my_list.append(Expression([]))
        self.assertEqual([Expression([Term('a')])], my_list)
    def testExpressionCreationFromMEDLINE(self):
        ex=Expression()
        ex.from_medline('Protein Interaction Mapping/*methods')
        self.assertEqual([Term('protein interaction mapping'),
                          Term('methods')],
                         ex.utterance)
    def testExpressionSetCreationFromMEDLINE(self):
        expset=ExpressionList()
        expset.from_medline(['Amanitins/*urine',
         '*Enzyme-Linked Immunosorbent Assay',
         'Female',
         'Humans',
         'Male',
         'Mushroom Poisoning/*urine',
         'Phalloidine/*poisoning',
         'Syndrome']
        ) # Straight from a random MEDLINE record
        should_look_like=ExpressionList()
        should_look_like.append(Expression([Term('amanitins'),
                                            Term('urine')]))
        should_look_like.append(Expression(
                                [Term('enzyme-linked immunosorbent assay')]))
        should_look_like.append(Expression([Term('female')]))
        should_look_like.append(Expression([Term('humans')]))
        should_look_like.append(Expression([Term('male')]))
        should_look_like.append(Expression([Term('mushroom poisoning'),
                                            Term('urine')]))
        should_look_like.append(Expression([Term('phalloidine'),
                                            Term('poisoning')]))
        should_look_like.append(Expression([Term('syndrome')]))
        self.assertEqual(should_look_like, expset)
    def testFlattenExpressionList(self):
        expset=ExpressionList().from_medline(['Amanitins/*urine',
         '*Enzyme-Linked Immunosorbent Assay',
         'Female',
         'Humans',
         'Male',
         'Mushroom Poisoning/*urine',
         'Phalloidine/*poisoning',
         'Syndrome']
        ) # Straight from a random MEDLINE record
        
        # Since the order is not guaranteed, we'll compare it as a set
        should_look_like=['amanitins', 'urine', 
                          'enzyme-linked immunosorbent assay',
                          'female', 'humans', 'male', 
                          'mushroom poisoning', 'phalloidine', 'poisoning',
                          'syndrome']
        self.assertEqual(set(should_look_like), set(expset.flatten()))
    def testMajorHeadings(self):
        expset=ExpressionList().from_medline(['Amanitins/*urine',
         '*Enzyme-Linked Immunosorbent Assay',
         'Female',
         'Humans',
         'Male',
         'Mushroom Poisoning/*urine',
         'Phalloidine/*poisoning',
         'Syndrome']
        ) # Straight from a random MEDLINE record
        
        # Since the order is not guaranteed, we'll compare it as a set
        should_look_like=['urine', 
                          'enzyme-linked immunosorbent assay',
                          'poisoning',
                          ]
        self.assertEqual(set(should_look_like), set(expset.major_headings()))

if __name__ == '__main__':
    unittest.main()