#!/usr/bin/env python
# encoding: utf-8
"""
semrep_graph_builder.py

Created by Jorge Herskovic on 2008-05-27.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""


from MEDRank.utility.logger import logging, ULTRADEBUG
from MEDRank.computation.graph_builder import GraphBuilder
from MEDRank.file.semrep import (EntityLine, RelationLine)

class SemrepGraphBuilder(GraphBuilder):
    """SEMREP files are described as three separate sets of lines: Text
    Lines (that we ignore), Relationship lines (that we want, because they
    describe the graph) and Entity lines (that describe the graph's
    nodes).
    This builder uses the relationship confidence as link strength. If there
    are more than two links between two nodes, their strengths get added."""
    def _create_graph(self, list_of_lines):
        """Actually build a graph from a list of SEMREP lines."""
        # Make a first pass through the list of lines gathering all 
        # known Entities and evaluate them to see if they qualify as Nodes
        logging.log(ULTRADEBUG, "Building a SEMREP graph from %r", list_of_lines)
        entity_gen=(x for x in list_of_lines if issubclass(type(x),
                                                           EntityLine))
        # We'll store the nodes by CUI for easy retrieval later.
        # Since SEMREP relationship lines use CUIs, we'll just index the
        # entities that way
        potential_graph_nodes={}
        for candidate_entity in entity_gen:
            new_node=self._node_factory(candidate_entity.CUI,
                                        candidate_entity.description,
                                        candidate_entity.confidence)
            if self.include_node(new_node):
                potential_graph_nodes[candidate_entity.CUI]=new_node
            else:
                logging.log(ULTRADEBUG, "Excluding %r from the graph.", new_node)
        # Now to build the graph and process the relationships
        # If a node doesn't exist in our Node database any relation containing
        # that node will have to be omitted (since we don't know about the 
        # node)
        relationship_gen=(x for x in list_of_lines if issubclass(type(x), 
                                                                RelationLine))
        new_graph=self._type_of_graph_to_build()
        for candidate_relation in relationship_gen:
            try:
                from_node=potential_graph_nodes[candidate_relation.CUI1]
                to_node=potential_graph_nodes[candidate_relation.CUI2]
            except KeyError:
                logging.log(ULTRADEBUG, "Relationship %r can't be part of the graph "
                              "because one of its candidate nodes was "
                              "filtered out.", candidate_relation)
                continue
            new_link=self._link_factory(from_node, to_node,
                                        candidate_relation.confidence,
                                        candidate_relation.relation_type)
            if self.include_link(new_link):
                new_graph.add_relationship(new_link)
            else:
                logging.log(ULTRADEBUG, "Excluding link %r from the graph.", new_link)
        return new_graph
