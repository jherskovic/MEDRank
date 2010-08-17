#!/usr/bin/env python
# encoding: utf-8
"""
metamap_cooccurrence_graph_builder.py

Created by Jorge Herskovic on 2008-05-27.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

from MEDRank.utility.logger import logging, ULTRADEBUG
from MEDRank.computation.graph_builder import GraphBuilder
from MEDRank.computation.graph_builder import GraphBuilderMeasure

class ArticleSentenceCount(GraphBuilderMeasure):
    """Represents the number of sentences in an article."""
    pass
    
class MetamapCooccurrenceGraphBuilder(GraphBuilder):
    """METAMAP files contain simply concepts. There are several ways of 
    establishing relationships between concepts; one is co-occurrence (terms
    that co-occur are related). 
    Another is creating one node per sentence and using those sentences
    to establish relationships, whose strength is similarity (see Mihalcea)
    
    This class creates large co-occurrence graphs, emulating the MEDRank v1
    behavior.
    """
    # Unfortunately, using Node and Link is extremely expensive for large
    # graphs with poor generation algorithms, so we simplify (a lot) and skip
    # using Node. Skipping Node implies an approximate 7x performance gain.
    def sentence_iterator(self, list_of_lines):
        """Iterates through the list of lines, returning a group with the
        same line_id each time.
        At the end of the iteration, the procedure updates the measurements
        of the graph builder to record the number of sentences it emitted."""
        current_group=[]
        current_id=None
        sentence_count=0
        for each_line in list_of_lines:
            if each_line.line_id!=current_id:
                # Is it the first time? If not, emit the current group
                if current_id is not None:
                    logging.log(ULTRADEBUG, "Emitting sentence %s with %d terms",
                                  current_id, len(current_group))
                    sentence_count+=1
                    yield current_group
                current_id=each_line.line_id
                current_group=[]
            current_group.append(each_line)
        # Are there lines left? Emit them
        if len(current_group)>0:
            logging.log(ULTRADEBUG, "Emitting last sentence %s with %d terms",
                          current_id, len(current_group))
            sentence_count+=1
            yield current_group
        
        # Iteration ended - record the measurement
        self._measurements.add(ArticleSentenceCount(sentence_count))
        return
                
    def _create_graph(self, list_of_lines):
        """Build a graph by generating a relationship for every pair of
        co-occurring nodes. We take advantage of the fact that (for our
        purposes) all lines with the same line_id in METAMAP output come from
        the same sentence."""
        new_graph=self._type_of_graph_to_build()
        logging.log(ULTRADEBUG, "Building a METAMAP co-occurrence graph from %r",
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
                    new_link=self._adirectional_link_factory(node1, node2,
                                           (node1.weight+node2.weight)/2.0)
                    if self.include_link(new_link):
                        new_graph.add_relationship(new_link)
                    else:
                        logging.log(ULTRADEBUG, "Excluding link %r from the graph",
                                      new_link)
        return new_graph

