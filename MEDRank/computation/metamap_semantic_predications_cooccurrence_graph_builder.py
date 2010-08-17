#!/usr/bin/env python
# encoding: utf-8
"""
metamap_semantic_predications_cooccurrence_graph_builder.py

Takes input data from MetaMap sentence by sentence, but creates graphs by using 
links from Cohen's Semantic Predication database. Items not covered by Cohen's 
SemPred DB are considered unrelated.

Created by Jorge Herskovic on 2010-01-12.
Copyright (c) 2010 University of Texas - Houston. All rights reserved.
"""

from MEDRank.file.semantic_predications import get_predications
from MEDRank.computation.metamap_cooccurrence_graph_builder import \
     MetamapCooccurrenceGraphBuilder
from MEDRank.utility.logger import logging, ULTRADEBUG

class MetamapSemanticPredicationsCooccurrenceGraphBuilder(
                MetamapCooccurrenceGraphBuilder):
    def _create_graph(self, list_of_lines):
        """Build a graph by generating a relationship for every pair of
        co-occurring nodes. We take advantage of the fact that (for our
        purposes) all lines with the same line_id in METAMAP output come from
        the same sentence."""
        new_graph=self._type_of_graph_to_build()
        logging.debug("Retrieving semantic predications for %r", 
                      self._line_set_id)
        try:
            predications=get_predications(self._line_set_id.pmid)
        except:
            logging.warn("No predications for %r", self._line_set_id)
            return new_graph
        logging.log(ULTRADEBUG, 
                    "Building a METAMAP co-occurrence graph from %r",
                    list_of_lines)
        for sentence in self.sentence_iterator(list_of_lines):
            # Each "sentence" contains a set of potential nodes that need
            # screening.
            nodes=[]
            for concept in sentence:
                new_node=self._node_factory(concept.CUI, 
                                            concept.description, 
                                            concept.confidence,
                                            concept.line)
                if self.include_node(new_node):
                    #nodes.append((concept.CUI, concept.confidence))
                    nodes.append(new_node)
                else:
                    logging.log(ULTRADEBUG, "%r excluded from the graph.", new_node)
            # Once we have all the nodes in a sentence, we generate all
            # possible combinations (O(n^2)), yes it's ugly.
            for i in xrange(len(nodes)):
                # Since relationships are not directional we can skip half
                # of the generation (i.e. if we have i<-->j we don't need
                # j<-->i
                for j in xrange(i+1, len(nodes)):
                    node1, node2=nodes[i],nodes[j] 
                    #new_link=AdirectionalLink(node1[0], node2[0], 
                    #                          (node1[1]+node2[1])/2.0)
                    # Is there a predication?
                    try:
                        this_link=predications[(node1, node2)]
                    except KeyError:
                        continue
                    new_link=self._adirectional_link_factory(node1, node2,
                                           this_link.weight)
                    if self.include_link(new_link):
                        new_graph.add_relationship(new_link)
                    else:
                        logging.log(ULTRADEBUG, "Excluding link %r from the graph",
                                      new_link)
        return new_graph
