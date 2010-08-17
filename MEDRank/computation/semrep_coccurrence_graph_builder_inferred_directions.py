#!/usr/bin/env python
# encoding: utf-8
"""
semrep_coccurrence_graph_builder_inferred_directions.py

Modifies SemrepCooccurrenceGraphBuilder by reviewing the list of generated 
directions and replacing adirectional relationships with inferred relational
ones.

Created by Jorge Herskovic on 2008-06-24.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

from MEDRank.utility.logger import logging, ULTRADEBUG
from MEDRank.computation.semrep_cooccurrence_graph_builder import (
    SemrepCooccurrenceGraphBuilder)
from MEDRank.computation.link import (Link, AdirectionalLink)
from MEDRank.computation.graph import Graph

class SemrepCooccurrenceGraphBuilderInferredDirections(
                                    SemrepCooccurrenceGraphBuilder):
    def __init__(self, type_of_graph_to_build=Graph, 
                 node_weight_threshold=0.0,
                 link_weight_threshold=0.0,
                 tf_idf_provider=None,
                 direction_inferrer=None):
        SemrepCooccurrenceGraphBuilder.__init__(self, type_of_graph_to_build,
                                                node_weight_threshold,
                                                link_weight_threshold,
                                                tf_idf_provider)
        self._inferrer=direction_inferrer
    def _create_graph(self, list_of_lines):
        graph=SemrepCooccurrenceGraphBuilder._create_graph(self,
                                                           list_of_lines)
        graph.consolidate_graph()
        new_graph=self._type_of_graph_to_build()
        for r in graph.relationships:
            direction=self._inferrer.infer_relation_direction(
                            r.node1.node_id, r.node2.node_id)
            if direction==0:
                # Just recycle the relationship
                new_relationship=r
            else:
                # The link constructors know what to do with negative weights
                # so we'll let them handle the directionality.
                new_relationship=self._link_factory(r.node1, r.node2,
                                                    r.weight*direction)
                logging.log(ULTRADEBUG, "Replacing %r by inferred relationship %r",
                              r, new_relationship)
            new_graph.add_relationship(new_relationship)
        return new_graph