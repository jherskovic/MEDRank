#!/usr/bin/env python
# encoding: utf-8
"""
base_hits_ranker.py

Created by Jorge Herskovic on 2008-06-18.
Copyright (c) 2008 University of Texas - Houston. All rights reserved.
"""

from MEDRank.utility.logger import logging, ULTRADEBUG
import operator
import time
from MEDRank.computation.ranker import (Ranker, RankerStats)

# Disable warnings about spaces before operators (they drive me crazy)
# pylint: disable-msg=C0322

# Some methods don't use self, which makes PyLint think they should
# be functions. I disagree for completeness reasons.
# pylint: disable-msg=R0201

class HITSRanker(Ranker):
    """Computes HITS as described in Kleinberg's seminal paper. 
    See Kleinberg, JM. Authoritative Sources in a Hyperlinked Environment"""
    @staticmethod
    def normalize_weights(weights):
        """Normalizes a numerical list, returning a copy of it."""
        maxw=float(max(weights))
        if maxw==0:
            return weights[:]
        return [x/maxw for x in weights]
    def i_operation(self, link_matrix, y_weights):
        """Computes Kleinberg's I operation on a vector of y-weights.
        It produces an x-vector that depends on the incoming links."""
        # Iterate over every incoming link for every node
        x_weights=[0.0] * len(link_matrix)
        for each_x in xrange(len(link_matrix)):
            this_x_weight=0.0
            for each_y in xrange(len(link_matrix)):
                if link_matrix[each_y, each_x]!=0:
                    this_x_weight+=y_weights[each_y]
            x_weights[each_x]=this_x_weight
        return x_weights
    def o_operation(self, link_matrix, x_weights):
        """Computes Kleinberg's O operation on a vector of x-weights.
        It produces a y-vector that depends on the outgoing links."""
        y_weights=[0.0] * len(link_matrix)
        for each_y in xrange(len(link_matrix)):
            this_y_weight=0.0
            for each_x in xrange(len(link_matrix)):
                if link_matrix[each_y, each_x]!=0:
                    this_y_weight+=x_weights[each_x]
            y_weights[each_y]=this_y_weight
        return y_weights
    def evaluate(self, link_matrix):
        """Perform an iterative computation of HITS"""
        logging.debug("Setting up to compute HITS on %r", link_matrix)
        # Sanity check
        if len(link_matrix)==0:
            raise ValueError("Attempting to HITS-rank an empty link matrix.")
        start=time.clock()
        logging.log(ULTRADEBUG, "Normalizing the link matrix.")
        # Perform actual computations on a normalized matrix
        try:
            normatrix=link_matrix.normalize()
        except ZeroDivisionError:
            raise ZeroDivisionError("Aberrant matrix: There are no links.")
        logging.log(ULTRADEBUG, "Iterating for HITS.")
        # Set up the iteration variables
        accumulator=2*self._e
        iterations=0
        x_w=[1.0]*len(normatrix)
        y_w=x_w[:]
        start_iter=time.clock() # Benchmarking
        while (accumulator>self._e):
            if iterations>self._max_iter:
                logging.debug("Reached the iteration limit of %d. Ending the "
                "HITS computation prematurely.", self._max_iter)
                break
            accumulator=0.0
            new_x_w=self.i_operation(normatrix, y_w)
            new_y_w=self.o_operation(normatrix, new_x_w)
            iterations+=1
            new_x_w=self.normalize_weights(new_x_w)
            new_y_w=self.normalize_weights(new_y_w)
            delta=zip(x_w, new_x_w) + zip(y_w, new_y_w)
            accumulator=reduce(operator.add, (abs(x[0]-x[1]) for x in delta))
            x_w=new_x_w
            y_w=new_y_w
        logging.log(ULTRADEBUG, "Iteration done.")
        finished_iter=time.clock()
        self._latest_stats=RankerStats(iterations, accumulator, start,
                                        start_iter, finished_iter)
        return (x_w, y_w)
        
