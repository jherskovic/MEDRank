#!/usr/bin/env python
# encoding: utf-8
"""
graph_builder.py

A GraphBuilder object takes a file (like a SEMREP file) represented as a 
LineList and builds the Nodes and Links necessary to create a Graph that we 
can later compute upon.

All knowledge about how to translate NLM output into Graphs should be 
isolated in this file.

Created by Jorge Herskovic on 2008-05-16.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import operator
from MEDRank.computation.graph import Graph
from MEDRank.computation.link import (Link, AdirectionalLink)
from MEDRank.computation.node import Node
from MEDRank.evaluation.result import Result
from MEDRank.evaluation.result_set import ResultSet
from MEDRank.utility.logger import (logging, ULTRADEBUG)

# Disable warnings about spaces before operators (they drive me crazy)
# pylint: disable-msg=C0322    
# pylint: disable-msg=R0201

class GraphBuilderMeasure(Result):
    """Represents a measurement performed by, or on, the graph builder."""
    pass
    
class ArticleLineCount(GraphBuilderMeasure):
    """Represents the number of lines in the article."""
    pass

class ArticleWordCount(GraphBuilderMeasure):
    """Represents the number of words in the article."""
    pass

class GraphBuilder(object):
    """GraphBuilder is a generic base class to derive. It provides a template
    to build the actual GraphBuilders, that should subclass this one. The
    design provides hooks to filter each node and link as it's considered, and
    those may be overridden by descendants to customize processing easily.
    
    The default filtering behavior is filtering by confidence (since it's
    something that will come in quite handy). 
    
    You can also specify whether to add the nodes that don't belong to a link
    back to the graph as nodes linked to themselves upon consolidation via the
    add_orphan_nodes parameter (it defaults to True)."""
    def __init__(self, type_of_graph_to_build=Graph, 
                 node_weight_threshold=0.0,
                 link_weight_threshold=0.0,
                 tf_idf_provider=None,
                 add_orphan_nodes=True):
        """Accepts a type of Graph to build (so we can use Graph subclasses
        without creating a separate hierarchy of GraphBuilder subclasses)"""
        self._type_of_graph_to_build=type_of_graph_to_build
        self._node_weight_threshold=node_weight_threshold
        self._link_weight_threshold=link_weight_threshold
        self._tf_idf=tf_idf_provider
        self._tf_idf_scores=None
        self._line_set_id=None
        self._node_cache=set([])
        self._add_orphan_nodes=add_orphan_nodes
        self._measurements=ResultSet()
    #Although at first glance the methods seem to be good candidates for
    #static methods, it's possible that descendants will want to take instance
    #variables into consideration when deciding how to process certain Nodes,
    #Links, or other input, so the methods will be regular member methods.
    def include_node(self, node_under_consideration):
        """Examines a node to decide whether it should be part of the graph.
        The default is to check the weight of all Node objects that wish to be
        part of the graph."""
        return (node_under_consideration.weight>=
                    self._node_weight_threshold)
    def include_link(self, link_under_consideration):
        """Examines a link to decide whether it should be part of the graph.
        The default is to check the strength of all Link objects that wish to
        be part of the graph."""
        return (link_under_consideration.weight>=
                    self._link_weight_threshold)
    def _preprocess_article(self, list_of_lines):
        """Makes a first pass through the article. This default implementation
        computes the TF*IDF values for the document, if a TF*IDF provider was 
        specified."""
        if self._tf_idf is not None:
            self._tf_idf.start_tf()
            for line in list_of_lines:
                self._tf_idf.tf_line(line)
            self._tf_idf_scores=self._tf_idf.end_tf()
        return
    def _node_factory(self, cui, description, weight, original_line=None):
        """Generates a new node. It will weight the node using the TF*IDF 
        provider, if one was specified."""
        # This function also mantains the internal node list
        new_node=Node(cui, description, weight, original_line)
        if self._tf_idf_scores is not None:
            new_node.weight=(new_node.weight*
                             self._tf_idf_scores[cui])
        self._node_cache.add(new_node)
        return new_node
    def _link_factory(self, node1, node2, weight, name=None):
        """Generates a new link."""
        return Link(node1, node2, weight, name)
    def _adirectional_link_factory(self, node1, node2, weight, name=None):
        """Generates a new adirectional link."""
        return AdirectionalLink(node1, node2, weight, name)
    def _create_graph(self, list_of_lines):
        """Actually build the graph (default implementation does nothing and
        returns an empty graph). Override in subclasses."""
        # pylint: disable-msg=W0613
        # Do something worthwhile
        return self._type_of_graph_to_build()
    def _post_process_graph(self, built_graph):
        """Post-processes the graph. The default implementation consolidates 
        it and adds orphan nodes to the graph, consolidating it again."""
        built_graph.consolidate_graph()
        self._tf_idf_scores=None # Make sure the scores aren't recycled 
                                 # accidentally
        if self._add_orphan_nodes:
            added=0
            rels=built_graph.relationships
            known_nodes=set([x.node1 for x in rels] + [x.node2 for x in rels])
            for n in self._node_cache:
                if n not in known_nodes:
                    added+=1
                    built_graph.add_relationship(
                            AdirectionalLink(n, n, n.weight))
            built_graph.consolidate_graph()
            logging.log(ULTRADEBUG, "Added %d orphan nodes", added)
        self._node_cache=set([])
        return built_graph
    def create_graph(self, list_of_lines):
        # Make sure that the measurements only reflect one run
        """Sets up the creation of a graph, ensuring that the metrics
        from the creation reflect only the latest run."""
        self._measurements=ResultSet()
        self._line_set_id=list_of_lines.set_id
        self._preprocess_article(list_of_lines.lines)
        graph=self._create_graph(list_of_lines.lines)
        graph=self._post_process_graph(graph)
        self._compute_measurements(list_of_lines.lines)
        return graph
    def _compute_measurements(self, list_of_lines):
        """Computes measurements on the lines the builder received, and the 
        graph building process."""
        self._measurements.add(ArticleLineCount(len(list_of_lines)))
        if len(list_of_lines)==0:
            wordcount=0
        else:
            wordcount=reduce(operator.add, (len(x.line.split()) for x in 
                                            list_of_lines))
        self._measurements.add(ArticleWordCount(wordcount))
    def get_measurements(self):
        """Getter for the measurements property"""
        return self._measurements
    measurements=property(get_measurements)