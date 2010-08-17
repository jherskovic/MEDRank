#!/usr/bin/env python
# encoding: utf-8
"""
test_graph_builder.py

Created by Jorge Herskovic on 2008-05-29.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import sys
import unittest
from MEDRank.computation.graph_builder import *
                
# pylint: disable-msg=C0103,C0111
class graph_builderTests(unittest.TestCase):
    def setUp(self):
        pass
    def testNodeFiltering(self):
        my_graph_builder=GraphBuilder(node_weight_threshold=0.5)
        my_fail_node=Node('a', 'b', 0.4)
        my_success_node=Node('b', 'c', 0.6)
        self.assertTrue(my_graph_builder.include_node(my_success_node))
        self.assertFalse(my_graph_builder.include_node(my_fail_node))
    def testLinkFiltering(self):
        my_graph_builder=GraphBuilder(link_weight_threshold=0.5)
        my_fail_node=Node('a', 'b', 0.6)
        my_success_node=Node('b', 'c', 0.6)
        a_link=Link(my_fail_node, my_success_node, 0.7)
        self.assertTrue(my_graph_builder.include_link(a_link))
        a_link=Link(my_fail_node, my_success_node, 0.3)
        self.assertFalse(my_graph_builder.include_link(a_link))
        
if __name__ == '__main__':
    unittest.main()