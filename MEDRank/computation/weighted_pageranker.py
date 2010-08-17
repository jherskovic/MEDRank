#!/usr/bin/env python
# encoding: utf-8
"""
weighted_pageranker.py

Created by Jorge Herskovic on 2008-05-10.
Copyright (c) 2008 University of Texas - Houston. All rights reserved.
"""

from MEDRank.computation.pageranker import PageRanker

class WeightedPageRanker(PageRanker):
    """Computes pagerank but takes into account the weight of the links
    between nodes, by using the matrix's value at i,j as a factor in the 
    computation."""
    def inner_formula(self, matrix_value, previous_pagerank, this_pagerank,
                      num_outgoing_links):
        """The inner part of the loop - override it for different versions
        of PageRank."""
        return this_pagerank+(previous_pagerank*matrix_value)\
                               /num_outgoing_links

