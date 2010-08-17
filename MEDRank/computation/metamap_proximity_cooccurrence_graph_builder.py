#!/usr/bin/env python
# encoding: utf-8
"""
metamap_proximity_cooccurrence_graph_builder.py

Builds a co-occurrence graph by assuming that elements that are adjacent in an
input stream were adjacent in the source file (this is true when using Machine Output
and when using regular Metamap output now)

Created by Jorge Herskovic on 2008-06-08.
Copyright (c) 2008 University of Texas - Houston. All rights reserved.
"""

from MEDRank.utility.logger import logging, ULTRADEBUG
from MEDRank.computation.graph_builder import GraphBuilder
from MEDRank.computation.node import Node
from MEDRank.computation.link import AdirectionalLink
from MEDRank.computation.graph import Graph
#from MEDRank.file.metamap_machine_output import (ConceptLine, 
#                                                 EndOfUtteranceLine)
from MEDRank.file.metamap import MetamapLine
from MEDRank.computation.metamap_cooccurrence_graph_builder import \
                                         MetamapCooccurrenceGraphBuilder
import math

class MetamapProximityCooccurrenceGraphBuilder(MetamapCooccurrenceGraphBuilder):
    """Build graphs based on METAMAP machine output, using proximity as a 
    proxy for links as expected by Mihalcea's TextRank algorithm. 
    If a direction_inferrer is passed, it will create a directional graph as
    directed by the inferrer."""
    def __init__(self, type_of_graph_to_build=Graph, 
                 node_weight_threshold=0.0,
                 link_weight_threshold=0.0,
                 tf_idf_provider=None,
                 link_strength=lambda x: 1.0/math.exp(x-1.0) if x>=0 and x<=10 else 0.0,
                 direction_inferrer=None):
        GraphBuilder.__init__(self, type_of_graph_to_build, 
                              node_weight_threshold, link_weight_threshold,
                              tf_idf_provider)
        self._link_strength=link_strength
        self._direction_inferrer=direction_inferrer
#    def sentence_iterator(self, list_of_lines):
#        """Breaks down metamap machine output into utterance->eou groups"""
#        current_group=[]
#        for each_line in list_of_lines:
#            if isinstance(each_line, EndOfUtteranceLine):
#                yield current_group
#                current_group=[]
#            else:
#                current_group.append(each_line)
#        if len(current_group)>0:
#            yield current_group
#        return
    def _create_graph(self, list_of_lines):
        new_graph=self._type_of_graph_to_build()
        logging.log(ULTRADEBUG,
                    "Building a METAMAP proximity co-occurrence graph "
                    "from %r", list_of_lines)
        # Iterate through each sentence, emitting links for each pair of
        # adjacent concepts (concept evaluators permitting)
        for sentence in self.sentence_iterator(list_of_lines):
            nodes=[]
            for concept in sentence:
                if not isinstance(concept, MetamapLine):
                    logging.log(ULTRADEBUG, "Skipping line %r, as it isn't a "
                                  "MetamapLine", sentence)
                    continue
                new_node=self._node_factory(concept.CUI, concept.description, 
                                            concept.confidence, concept.line)
                if self.include_node(new_node):
                    nodes.append(new_node)
                    logging.log(ULTRADEBUG, "%r included in the graph", new_node)
                else:
                    logging.log(ULTRADEBUG, "%r excluded from the graph", new_node)
            for i in xrange(len(nodes)-1):
                for j in xrange(i+1, len(nodes)):
                    # Adjacent nodes are related more in this model. 
                    # The weight of the relationship is given by the distance
                    node1, node2=nodes[i], nodes[j]
                    if self._direction_inferrer is None:
                        new_link=self._adirectional_link_factory(node1, node2, 
                                                    self._link_strength(j-i))
                    else:
                        new_dir=\
                          self._direction_inferrer.infer_relation_direction(
                           node1.node_id, node2.node_id)
                        if new_dir==0:
                            new_link=self._adirectional_link_factory(node1,
                                                                     node2, 
                                                self._link_strength(j-i))
                        else:
                            new_link=self._link_factory(node1, node2,
                                        new_dir*self._link_strength(j-i))
                            
                    if self.include_link(new_link):
                        new_graph.add_relationship(new_link)
                    else:
                        logging.log(ULTRADEBUG, "Excluding link %r from the graph", 
                                      new_link)
        return new_graph
