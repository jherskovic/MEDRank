#!/usr/bin/env python
# encoding: utf-8
"""
link_matrix.py

Created by Jorge Herskovic on 2008-05-09.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import operator
from MEDRank.computation.base_matrix import Matrix

# pylint: disable-msg=C0111,E0211,C0111,W0212,W0612
class LinkMatrix(Matrix):
    """Represents a set of links from one node to another. Actually stores the
    count of links from one node to another in each cell, such that m[i, j] is
    the number of links from i to j."""
    def neighbors(self, i):
        """Returns the list of neighbors of a node i (this is the list of
        non-zero indexes for the i-th row of the matrix)"""
        # Zip the proper row with its indices, and extract the non-zero ones
        return [x[1] for x in zip(self[i].tolist()[0], xrange(self[i].size)) 
                                  if x[0]>0]
    def all_neighbors(self):
        """Returns all the neighbors of each node."""
        return [self.neighbors(x) for x in xrange(self.shape[0])]
