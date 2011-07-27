#!/usr/bin/env python
# encoding: utf-8
"""
spread_activation.py

Created by Jorge Herskovic on 2011-01-20.
Copyright (c) 2011 UTHSC School of Health Information Sciences. All rights reserved.
"""

import time
import copy
from MEDRank.utility.logger import logging, ULTRADEBUG
from MEDRank.computation.link_matrix import LinkMatrix
from MEDRank.computation.ranker import (Ranker, RankerStats)

class SpreadingActivation(Ranker):
    """Describes a SpreadingActivation ranker.
       It is a class that will perform an iterative PageRank computation with
       a maximum number of iterations, until convergence (as described by
       epsilon) or max_iterations is reached.
              
       The only real differences between this and PageRank are:
       -the starting values for the computation. For PageRank, they are 1. 
        For SpreadingActivation, they are whatever the e_vector states.
       -the e_vector does not feed into the nodes every iteration, unlike it
       -does on PageRank
              
       Call the evaluate() method to start the evaluation. The evaluation 
       should always return normalized scores (i.e. between 0 and 1)"""
    def inner_formula(self, matrix_value, previous_pagerank, this_pagerank,
                      num_outgoing_links):
        """The inner part of the loop - override it for different versions
        of PageRank."""
        # While the current formula could be a static method, other inner
        # formulas may rely on instance data - hence it's not.
        return this_pagerank+previous_pagerank/num_outgoing_links
    def evaluate(self, linkmatrix, e_vector):
        """Perform an iterative Spreading Activation computation on a
        link matrix."""
        # Cache commonly used values
        logging.log(ULTRADEBUG, "Setting up to compute PageRank on %r", linkmatrix)
        # Sanity check
        if len(linkmatrix)==0:
            raise ValueError("Attempting to PageRank an empty link matrix.")
            
        start=time.clock()
        
        # Precompute the total number of outgoing links for each node (this
        # is the number of non-zero entries in the node's row of the link
        # matrix)
        count_outgoing_links=[linkmatrix.row_nonzero(x)
                              for x in xrange(len(linkmatrix))]
        
        # The incoming links of each node are the nodes that point TO it, 
        # that is, for every lm[i,j]!=0 in the matrix there's an incoming
        # link to j. To figure out the incoming links, then, we need to 
        # traverse the neighborhood of every node looking for incoming links 
        # to each j. The easy way to do this is to transpose the matrix and
        # then get the neighborhoods
        incoming_links=linkmatrix.transpose().all_neighbors()
        
        # Set up the iteration - the PageRank computation ends when the 
        # difference between successive iterations is smaller than epsilon.
        accumulator=2*self._e
        iterations=0
        pagerank_values=copy.copy(e_vector)
        logging.log(ULTRADEBUG, "Setup done. Beginning iterations.")
        
        # Use a normalized matrix for the actual computations
        try:
            normatrix=linkmatrix.normalize()
        except ZeroDivisionError:
            raise ZeroDivisionError("Aberrant matrix: There are no links.")
        start_iter=time.clock()
        
        # Iterate until the difference between iterations is smaller than 
        # epsilon. In each iteration, go over every node, computing its 
        # PageRank based on the PageRank of the adjacent nodes (see the
        # Brin & Page paper for the formula)
        while (accumulator>self._e):
            if iterations>self._max_iter:
                logging.debug("Reached the iteration limit of %d. Ending the "
                "PageRank computation prematurely.", self._max_iter)
                break
            accumulator=0.0
            new_pagerank_values=pagerank_values[:]
            for i in xrange(len(linkmatrix)):
                this_pagerank=0.0
                for j in incoming_links[i]:
                    #this_pagerank+=((pagerank_values[j]*nm[j,i])/
                    #                count_outgoing_links[j])
                    #this_pagerank+=(pagerank_values[j]/
                    #                count_outgoing_links[j])
                    this_pagerank=self.inner_formula(normatrix[j, i],
                                                     pagerank_values[j],
                                                     this_pagerank,
                                                     count_outgoing_links[j])
                new_pagerank_values[i]=(self._d*this_pagerank)
                accumulator+=abs(new_pagerank_values[i]-pagerank_values[i])
            iterations+=1
            pagerank_values=new_pagerank_values
        finished_iter=time.clock()
        # Benchmarking and book-keeping
        self._latest_stats=RankerStats(iterations, accumulator, start,
                                        start_iter, finished_iter)
        
        logging.log(ULTRADEBUG, "Finished computation.")
        highest=max(pagerank_values)
        if highest==0.0:
            raise ValueError("PageRank returned all zeros.")
        # Normalize the scores
        return [x/highest for x in pagerank_values]
