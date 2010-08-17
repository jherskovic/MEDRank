#!/usr/bin/env python
# encoding: utf-8
"""
single_item_workflow.py

Contains a skeleton class for the workflow on a single item (whatever that item
may be) that should be subclassed to work on 

Created by Jorge Herskovic on 2010-06-25.
Copyright (c) 2010 UTHSC School of Health Information Sciences. All rights reserved.
"""

# pylint: disable-msg=C0322
from MEDRank.utility.logger import logging, ULTRADEBUG
from MEDRank.computation.mapped_ranker import MappedRanker
from MEDRank.utility.workflow import CouldNotRank

class SingleItemWorkflow(object):
    """Contains a skeleton simple workflow through the system for a single 
    item (i.e. a document, clinical note, article, etc.). It expects a
    graph builder constructor, its parameter set, a ranker constructor, its
    parameter set, and a ranking cutoff. (Otherwise, why are you using MEDRank?)
    
    Parameters:
    graph_builder_constructor: A class that knows how to build a Graph (as in
                               MEDRank.computation.graph.Graph)
    graph_builder_params:   The parameters you want to use to call the 
                            aforementioned constructor.
    ranker_constructor:     A class that knows how to build a Ranker (as in
                            MEDRank.computation.ranker.Ranker) or descendant
    ranker_params: The parameters to pass to THAT constructor
    ranking_cutoff: A float value between 0.0 (no filtering) and 1.0. 
                   Everything below ranking_cutoff gets discarded.
    """
    def __init__(self, graph_builder_constructor, graph_builder_params,
                 ranker_constructor, ranker_params, ranking_cutoff):
        logging.debug("Setting up a SingleItemWorkflow instance.")
        logging.debug("My graph builder is: %r", graph_builder_constructor)
        if graph_builder_constructor is not None:
            self._graph_builder=\
                graph_builder_constructor(*graph_builder_params)
        else:
            self._graph_builder=None    
        if ranker_constructor is not None:
            self._ranker=MappedRanker(ranker_constructor(*ranker_params))
        else:
            self._ranker=None
        logging.debug("My ranker is: %r", ranker_constructor)
        self._ranking_cutoff=ranking_cutoff
        logging.debug("My ranking cutoff is: %r", self._ranking_cutoff)
        self.all_results={}
        return
    def __repr__(self):
        return "<%s instance>" % self.__class__.__name__
    def graph_item(self, item):
        if self._graph_builder is None:
            return None
        return self._graph_builder.create_graph(item)
    def graph_and_rank(self, item):
        """Turn the item into a graph, then a link matrix, and then rank
        it. Returns the ranked list of nodes."""
        item_graph=self.graph_item(item)
        logging.log(ULTRADEBUG, "The item graph is %r.", item_graph)
        item_matrix=item_graph.as_mapped_link_matrix()
        if len(item_matrix)==0:
            logging.info("Skipping item %r. It has an empty matrix.", 
                         item)
            raise CouldNotRank("Item %r is not rankable." % item)
        try:
            ranked_item=self._ranker.evaluate(item_matrix)
        except ValueError:
            logging.info("%r returned an exception while ranking %r. "
                         "Skipping.", self._ranker, item)
            raise CouldNotRank("There was an exception while ranking %r." %
                                item)
        return ranked_item
    def include_item(self, item):
        """Should this item be included in the sample? Return a boolean
        specifying so. Override to customize."""
        return True
    def process_item(self, one_item):
        if not self.include_item(one_item):
            logging.log(ULTRADEBUG, "Skipping item %r due to exclusion "
                          " criteria.", one_item)
            return
        try:
            ranked_item=self.graph_and_rank(one_item)
        except CouldNotRank:
            return
        cut_item=[x for x in ranked_item if x[1] >= self._ranking_cutoff]
        # Unify the result sets
        self.all_results[one_item.set_id]=cut_item
        return
        