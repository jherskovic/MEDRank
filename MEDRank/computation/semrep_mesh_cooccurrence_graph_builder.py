#!/usr/bin/env python
# encoding: utf-8
"""
semrep_cooccurrence_graph_builder.py

Created by Jorge Herskovic on 2008-05-27.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

from MEDRank.utility.logger import logging, ULTRADEBUG
from MEDRank.computation.metamap_cooccurrence_graph_builder import \
                                    MetamapCooccurrenceGraphBuilder
from MEDRank.computation.node import Node
from MEDRank.file.semrep_mesh import (EntityMeSHLine)

class MeshNode(Node):
    __slots__=['_mesh']
    def __init__(self, node_id, node_name, node_weight, mesh_expression):
        Node.__init__(self, node_id, node_name, node_weight)
        self._mesh=mesh_expression
    def get_mesh(self):
        return self._mesh
    mesh=property(get_mesh)
    def __eq__(self, other):
        return self._mesh==other._mesh
    def __ne__(self, other):
        return self._mesh!=other._mesh
    def __hash__(self):
        return hash(self._mesh)

class SemrepMeSHCooccurrenceGraphBuilder(MetamapCooccurrenceGraphBuilder):
    """Builds graphs based on SEMREP output using just entity co-occurrence 
    (i.e. two entities are related if they are next to each other.)
    It's a subclass of MetamapCoccurrenceGraphBuilder to recycle the sentence
    iterator."""
    def _node_factory(self, cui, description, weight, mesh_expression):
        # Use inherited behavior
        base_node=MetamapCooccurrenceGraphBuilder._node_factory(self, 
                                                               cui,
                                                               description,
                                                               weight)
        new_node=MeshNode(base_node.node_id, base_node.name, base_node.weight,
                          mesh_expression)
        return new_node
    def _create_graph(self, list_of_lines):
        new_graph=self._type_of_graph_to_build()
        logging.log(ULTRADEBUG, "Building a SEMREP co-occurrence graph from %r", 
                      list_of_lines)
        # Iterate through each sentence, emitting links for each pair of
        # adjacent concepts (concept evaluators permitting)
        for sentence in self.sentence_iterator(list_of_lines):
            nodes=[]
            for concept in sentence:
                if not isinstance(concept, EntityMeSHLine):
                    logging.log(ULTRADEBUG, "Skipping line %r, as it isn't an "
                                  "EntityMeSHLine", concept)
                    continue
                new_node=self._node_factory(concept.CUI, concept.description, 
                                            concept.confidence, concept.mesh)
                if self.include_node(new_node):
                    nodes.append(new_node)
                else:
                    logging.log(ULTRADEBUG, "%r excluded from the graph", new_node)
            for i in xrange(len(nodes)-1):
                # Adjacent nodes are related in this model. 
                node1, node2=nodes[i:i+2]
                new_link=self._adirectional_link_factory(node1, node2, 
                                          (node1.weight+node2.weight)/2.0)
                if self.include_link(new_link):
                    new_graph.add_relationship(new_link)
                else:
                    logging.log(ULTRADEBUG, "Excluding link %r from the graph", 
                                  new_link)
        return new_graph

