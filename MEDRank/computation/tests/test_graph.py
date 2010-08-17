#!/usr/bin/env python
# encoding: utf-8
"""
graph.py

Created by Jorge Herskovic on 2008-05-29.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import sys
from MEDRank.file.semrep import (EntityLine, RelationLine)
from MEDRank.computation.graph import *
from MEDRank.computation.link import Link
from MEDRank.computation.node import Node
import unittest
import operator

# pylint: disable-msg=C0103,C0111,R0904,W0212
class graphTests(unittest.TestCase):
    def setUp(self):
        """The basic test's graph structure will describe 5 
         nodes with the following links between them:
         (this is the same graph used to test the pagerankers)
             (0)-->(1)-->(2)-->(3)<--(4)
              ↑            ╲__ ↗|
              └─────────────────┘
              
        Note that, even though the Nodes are different objects, their 
        equality properties make them indistinguishable (it might still be
        reasonable to use the same objects in a real graph instead of in
        the tests!)
        """
        self.test_graph=Graph()
    @staticmethod
    def fill_in_graph(a_graph, link_type=Link):
        a_graph.add_relationship(link_type(Node('0', 'Node0', 1),
                                           Node('1', 'Node1', 1),
                                           1.0))
        a_graph.add_relationship(link_type(Node('1', 'Node1', 1),
                                           Node('2', 'Node2', 1),
                                           1.0))
        a_graph.add_relationship(link_type(Node('2', 'Node2', 1),
                                           Node('3', 'Node3', 1),
                                           1.0))
        a_graph.add_relationship(link_type(Node('2', 'Node2', 1),
                                           Node('3', 'Node3', 1),
                                           1.0))
        a_graph.add_relationship(link_type(Node('3', 'Node3', 1),
                                           Node('4', 'Node4', 1),
                                           -1.0))
        a_graph.add_relationship(link_type(Node('3', 'Node3', 1),
                                           Node('0', 'Node0', 1),
                                           1.0))
        a_graph.consolidate_graph()
    def testGraphConstruction(self):
        self.fill_in_graph(self.test_graph)
        #self.assertEqual(5, len(self.test_graph._entities))
        # There should be 5 relationships, too (one should've been discarded)
        self.assertEqual(5, len(self.test_graph._relationships))
    def testAlternateRelationshipHandler(self):
        class additiveRelHandler(Graph):
            @staticmethod
            def relationship_collision_handler(old_ones):
                return Link(old_ones[0].node1, old_ones[0].node2, 
                            reduce(operator.add, 
                                [x.weight for x in old_ones]))
        my_test_graph=additiveRelHandler()
        self.fill_in_graph(my_test_graph)
        #self.assertEqual(5, len(self.test_graph._entities))
        # There should be 5 relationships, too (one should've been discarded)
        self.assertEqual(5, len(my_test_graph._relationships))
        # Get the corresponding node
        changed_node=[x for x in my_test_graph._relationships 
                      if x.node1.node_id=='2' and x.node2.node_id=='3'][0]
        # Yes, retrieving nodes and links is very convoluted. I don't expect
        # it to be a frequent operation.
        self.assertEqual(changed_node.weight, 2.0)
    def testLinkMatrixConversion(self):
        self.fill_in_graph(self.test_graph)
        a_matrix=self.test_graph.as_mapped_link_matrix()
        self.assert_(type(a_matrix) is MappedLinkMatrix)
        from_node=Node('2', 'Node2', 1)
        to_node=Node('4', 'Node4', 1)
        self.assertEqual(a_matrix[a_matrix.get_term_position(from_node),
                                  a_matrix.get_term_position(to_node)],
                         0.0)
        from_node=Node('3', 'Node3', 1)
        # There's no relation from 3 to 4 - it's from 4 to 3 (it was negative)
        self.assertEqual(a_matrix[a_matrix.get_term_position(from_node),
                                  a_matrix.get_term_position(to_node)],
                                  0.0)
        self.assertEqual(a_matrix[a_matrix.get_term_position(to_node),
                                  a_matrix.get_term_position(from_node)],
                                  1.0)
    def testConvertEmptyGraph(self):
        matrix=self.test_graph.as_mapped_link_matrix()
        self.assertEqual(0, len(matrix))
    def testConvertingAdirectionalGraph(self):
        self.fill_in_graph(self.test_graph, AdirectionalLink)
        a_matrix=self.test_graph.as_mapped_link_matrix()
        self.assert_(type(a_matrix) is MappedLinkMatrix)
        from_node=Node('2', 'Node2', 1)
        to_node=Node('4', 'Node4', 1)
        self.assertEqual(a_matrix[a_matrix.get_term_position(from_node),
                                  a_matrix.get_term_position(to_node)],
                         0.0)
        from_node=Node('3', 'Node3', 1)
        # There's no relation from 3 to 4 in the directional matrix
        # but there should be one here
        self.assertEqual(a_matrix[a_matrix.get_term_position(from_node),
                                  a_matrix.get_term_position(to_node)],
                                  1.0)
        self.assertEqual(a_matrix[a_matrix.get_term_position(to_node),
                                  a_matrix.get_term_position(from_node)],
                                  1.0)
    def test_ncol(self):
        self.fill_in_graph(self.test_graph, AdirectionalLink)
        self.assertEquals(self.test_graph.as_ncol_file(), 
        """Node0 Node1 1.0000000
Node2 Node3 1.0000000
Node1 Node2 1.0000000
Node3 Node4 1.0000000
Node3 Node0 1.0000000""")
        
if __name__ == '__main__':
    unittest.main()