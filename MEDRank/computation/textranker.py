#!/usr/bin/env python
# encoding: utf-8
"""
textranker.py

Implements the TextRank computation as described by Mihalcea (2004)

Created by Jorge Herskovic on 2008-05-17.
Copyright (c) 2008 University of Texas - Houston. All rights reserved.
"""

import time
from MEDRank.utility.logger import logging, ULTRADEBUG
from MEDRank.computation.ranker import (Ranker, RankerStats)
from MEDRank.computation.link_matrix import LinkMatrix

class TextRanker(Ranker):
    """Perform Rada Mihalcea's TextRank computation on a link matrix"""
    def inner_formula(self, matrix_value, previous_textrank, this_textrank,
                      weights_neighbors):
        """The inner part of the loop - override for custom TextRankers"""
        return this_textrank+(matrix_value/weights_neighbors)*\
            previous_textrank
    def evaluate(self, linkmatrix, e_vector=None):
        """Perform an iterative computation of TextRank"""
        logging.log(ULTRADEBUG, "Setting up to compute TextRank on %r", linkmatrix)
        # Sanity check
        if len(linkmatrix)==0:
            raise ValueError("Attempting to PageRank an empty link matrix.")
        start=time.clock()
        logging.log(ULTRADEBUG, "Normalizing the link matrix.")
        # Perform actual computations on a normalized matrix
        try:
            normatrix=linkmatrix.normalize()
        except ZeroDivisionError:
            raise ZeroDivisionError("Aberrant matrix: There are no links.")
        # Precompute the neighborhood of each node
        logging.log(ULTRADEBUG, "Computing all neighborhoods.")
        neighborhood=linkmatrix.all_neighbors()
        logging.log(ULTRADEBUG, "Computing the weight of each neighborhood.")
        neighborhood_weights=[0.0]*len(linkmatrix)
        for i in xrange(len(linkmatrix)):
            this_neighbor=0.0
            for j in neighborhood[i]:
                this_neighbor+=normatrix[i, j]
            neighborhood_weights[i]=this_neighbor
        
        logging.log(ULTRADEBUG, "Weight computation done - iterating.")
        # Set up the iteration variables
        accumulator=2*self._e
        iterations=0
        textrank=[1.0]*len(linkmatrix)
        start_iter=time.clock() # Benchmarking
        while (accumulator>self._e):
            if iterations>self._max_iter:
                logging.log(ULTRADEBUG, "Reached the iteration limit of %d. Ending the "
                "TextRank computation prematurely.", self._max_iter)
                break
            accumulator=0.0
            new_textrank=textrank[:]
            for i in xrange(len(normatrix)):
                this_textrank=0.0
                for j in neighborhood[i]:
                    this_textrank=self.inner_formula(normatrix[j, i],
                                                     textrank[j],
                                                     this_textrank,
                                                     neighborhood_weights[j])
                new_textrank[i]=1-self._d+self._d*this_textrank
                accumulator+=abs(new_textrank[i]-textrank[i])
            iterations+=1
            textrank=new_textrank
        logging.log(ULTRADEBUG, "Iteration done.")
        finished_iter=time.clock()
        self._latest_stats=RankerStats(iterations, accumulator, start,
                                        start_iter, finished_iter)
        highest=max(textrank)
        if highest==0.0:
            raise ValueError("TextRank returned all zeros!")
        return [x/highest for x in textrank]
        
