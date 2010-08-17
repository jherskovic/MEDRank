#!/usr/bin/env python
# encoding: utf-8
"""
test_tree_node.py

Created by Jorge Herskovic on 2008-05-29.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import unittest
from MEDRank.mesh.tree_node import *

# pylint: disable-msg=C0103,C0111,R0904        
class tree_nodeTests(unittest.TestCase):
    def setUp(self):
        self.my_tree_node=TreeNode('myocardial infarction', 'ct', 'qualifier',
                                    set(['C01.785']))
    def testTypeChecking(self):
        exception_raised=False
        try:
            TreeNode('m', 't', None)
        except TypeError:
            exception_raised=True
        self.assertEqual(exception_raised, True)
    def testPositionSetting(self):
        exception_raised=False
        try:
            self.my_tree_node.position=self.my_tree_node.position|set(['a'])
        except TypeError:
            exception_raised=True
        self.assertEqual(exception_raised, False)
        try:
            self.my_tree_node.position=self.my_tree_node.position+'a'
        except TypeError:
            exception_raised=True
        self.assertEqual(exception_raised, True)
    def testUniqueness(self):
        self.assertEqual(self.my_tree_node.get_trees(), set(['C']))
        self.my_tree_node.position|=set(['D10'])
        self.assertEqual(self.my_tree_node.get_trees(), set(['C', 'D']))
        self.my_tree_node.position|=set(['C10'])
        self.assertEqual(self.my_tree_node.get_trees(), set(['C', 'D']))
    def testDepths(self):
        self.assertEqual([1], self.my_tree_node.depths())
        self.my_tree_node.position|=set(['D10'])
        self.assertEqual([0, 1], self.my_tree_node.depths())
        self.my_tree_node.position|=set(['D10.154.678.901'])
        self.assertEqual([0, 1, 3], self.my_tree_node.depths())
        self.assertEqual(0, self.my_tree_node.shallowest_depth())
        self.assertEqual(3, self.my_tree_node.deepest_depth())
    def testPositions(self):
        self.my_tree_node.position|=set(['D10.154.678.901'])
        self.assertEquals(self.my_tree_node.shallowest_position(), 'C01.785')
        self.assertEquals(self.my_tree_node.deepest_position(), 
                          'D10.154.678.901')
    def testNotDescriptor(self):
        self.assert_(self.my_tree_node.is_descriptor() is False)
    def testNotQualifier(self):
        self.assert_(self.my_tree_node.is_qualifier() is False)
    def testDescriptor(self):
        a_node=TreeNode('Some Descriptor', 'mh', 'dummy', set(['D123456789']))
        self.assert_(a_node.is_descriptor() is True)
    def testQualifier(self):
        a_node=TreeNode('Some qualifier', 'qq', 'dummy', set(['Q987556421']))
        self.assert_(a_node.is_qualifier() is True)

if __name__ == '__main__':
    unittest.main()