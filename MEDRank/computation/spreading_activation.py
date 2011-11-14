#!/usr/bin/env python
# encoding: utf-8
"""
spread_activation.py

Created by Jorge Herskovic on 2011-01-20.
Copyright (c) 2011 UTHSC School of Health Information Sciences. All rights reserved.
"""

import time
from MEDRank.utility.logger import logging, ULTRADEBUG
from MEDRank.computation.ranker import (Ranker, RankerStats)
import numpy

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
        return this_pagerank + previous_pagerank / num_outgoing_links
    def evaluate(self, linkmatrix, e_vector):
        """Perform an iterative Spreading Activation computation on a
        link matrix."""
        # Cache commonly used values
        logging.log(ULTRADEBUG, "Setting up to compute PageRank on %r", linkmatrix)
        # Sanity check
        if len(linkmatrix) == 0:
            raise ValueError("Attempting to PageRank an empty link matrix.")
        
        if self._max_iter > 100:
            logging.warn("Unusually large number of iterations (%d) for spreading activation."
                         "I hope you know what you're doing!", self._max_iter)
        
        start = time.clock()
        
        # Precompute the total number of outgoing links for each node (this
        # is the number of non-zero entries in the node's row of the link
        # matrix)
        count_outgoing_links = numpy.array([linkmatrix.row_nonzero(x)
                              for x in xrange(len(linkmatrix))], dtype=numpy.int_)
        
        # The incoming links of each node are the nodes that point TO it, 
        # that is, for every lm[i,j]!=0 in the matrix there's an incoming
        # link to j. To figure out the incoming links, then, we need to 
        # traverse the neighborhood of every node looking for incoming links 
        # to each j. The easy way to do this is to transpose the matrix and
        # then get the neighborhoods
        incoming_links = linkmatrix.transpose().all_neighbors()
        
        # Set up the iteration - the PageRank computation ends when the 
        # difference between successive iterations is smaller than epsilon.
        accumulator = 2 * self._e
        iterations = 0
        activation_values = numpy.array(e_vector[:])
        logging.log(ULTRADEBUG, "Setup done. Beginning iterations.")
        
        # Use a normalized matrix for the actual computations
        try:
            normatrix = linkmatrix.normalize()
        except ZeroDivisionError:
            raise ZeroDivisionError("Aberrant matrix: There are no links.")
        start_iter = time.clock()
        
        # Iterate until the difference between iterations is smaller than 
        # epsilon. In each iteration, go over every node, computing its 
        # PageRank based on the PageRank of the adjacent nodes (see the
        # Brin & Page paper for the formula)
        while (accumulator > self._e):
            if iterations > self._max_iter:
                logging.debug("Reached the iteration limit of %d. Ending the "
                "Spreading activation.", self._max_iter)
                break
            accumulator = 0.0
            logging.log(ULTRADEBUG, "Iteration: %d, activation: %r", iterations, activation_values)
            new_activation_values = numpy.copy(activation_values)
            for i in xrange(len(linkmatrix)):
                activation = 0.0
                for j in incoming_links[i]:
                    #activation+=((activation_values[j]*nm[j,i])/
                    #                count_outgoing_links[j])
                    #activation+=(activation_values[j]/
                    #                count_outgoing_links[j])
                    activation = self.inner_formula(normatrix[j, i],
                                                     activation_values[j],
                                                     activation,
                                                     count_outgoing_links[j])
                # TODO: Fix this, activation not accumulating cleanly.
                new_activation_values[i] = new_activation_values[i] + (self._d * activation)
                accumulator += abs(new_activation_values[i] - activation_values[i])
            iterations += 1
            # Test for infinity and abort the calculation if we overflow
            if not numpy.isfinite(new_activation_values).all():
                logging.warn("Spreading activation finished prematurely because of an overflow after iteration %d.",
                             iterations)
                break
            activation_values = new_activation_values
        finished_iter = time.clock()
        # Benchmarking and book-keeping
        self._latest_stats = RankerStats(iterations, accumulator, start,
                                        start_iter, finished_iter)
        
        logging.log(ULTRADEBUG, "Finished computation.")
        highest = max(activation_values)
        if highest == 0.0:
            raise ValueError("Spreading activation returned all zeros.")
        # Normalize the scores
        return [x/highest for x in activation_values]
        