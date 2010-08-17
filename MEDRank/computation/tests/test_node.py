#!/usr/bin/env python
# encoding: utf-8
"""
test_node.py

Created by Jorge Herskovic on 2008-05-29.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import unittest
#sys.path.append('../')
from MEDRank.computation.node import *

# pylint: disable-msg=C0103,C0111,R0904        
class nodeTests(unittest.TestCase):
    def setUp(self):
        self.n=Node("c1234", "Fake node", 0.987)
    def testName(self):
        self.assertEquals("Fake node", self.n.name)
    def testid(self):
        self.assertEquals("c1234", self.n.node_id)
    def testWeight(self):
        self.assertEquals(0.987, self.n.weight)
    def testEquivalence(self):
        # The set properties of the nodes are extremely important, so they
        # will be tested. Nodes must be hashable and equivalence-tested.
        self.assertEqual(self.n, Node("c1234", "Fake node", 0.123))
    def testSetBehavior(self):
        my_nodes=set([self.n])
        self.assertEqual(1, len(my_nodes))  
        # Shouldn't create a new node      
        my_nodes.add(Node("c1234", "Fake node", 0.123)) 
        self.assertEqual(1, len(my_nodes))
        # Should've kept the original node. Test that.
        self.assertEqual([x for x in my_nodes][0].weight, 0.987)
        my_nodes.add(Node("c1235", "Fake node", 0.123)) 
        self.assertEqual(2, len(my_nodes))
        
        
        
if __name__ == '__main__':
    unittest.main()
