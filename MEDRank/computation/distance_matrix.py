#!/usr/bin/env python
# encoding: utf-8
"""
distance_matrix.py

See Dhyani D., Ng W.K., and Bhowmick S.S. "A survey of Web Metrics"

Creates and mantains a distance matrix from a link matrix.

Created by Jorge Herskovic on 2008-06-19.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""
from MEDRank.utility.logger import logging, ULTRADEBUG
import os.path
import sys
from MEDRank.computation.base_matrix import Matrix
from ctypes import cdll, CDLL, byref
# Disable warnings about spaces before operators (they drive me crazy)
# pylint: disable-msg=C0322

LIBRARY_LOCATION=os.path.join(sys.exec_prefix, 'lib', 
                              'python'+sys.version[:3],
                              'site-packages', 'MEDRank', 'computation',
                              '_distmat.so')
cdll.LoadLibrary(LIBRARY_LOCATION)
DISTLIB=CDLL(LIBRARY_LOCATION)

class DistanceMatrix(object):
    """Represents a distance matrix, in which each C[i, j] encodes the 
    distance from i to j in a graph.
    Pass the value you plan on using as an unreachable distance to the 
    constructor. If you omit it, it will default to the link matrix's size
    (reasonable in most cases).
    
    The distance matrix is meant to compute stats on, so it's immutable by
    design.
    """
    def __init__(self, a_link_matrix, unreachable_distance=None):
        self._matrix=Matrix(len(a_link_matrix))
        if unreachable_distance is None:
            unreachable_distance=len(a_link_matrix)
        self._unreachable=unreachable_distance
        logging.log(ULTRADEBUG, "Getting C versions of the matrices.")
        transposed=a_link_matrix.transpose()
        transposed_c=transposed.as_binary_c_matrix()
        c_link_matrix=a_link_matrix.as_binary_c_matrix()
        to_fill_in=self._matrix.as_binary_c_matrix()
        logging.log(ULTRADEBUG, "Going into C to perform the search.")
        DISTLIB.fill_distance_matrix(byref(to_fill_in), byref(c_link_matrix), 
                                     byref(transposed_c), len(a_link_matrix),
                                     self._unreachable)
        logging.log(ULTRADEBUG, "Back from C. Filling the matrix in.")
        self._matrix.fill_from_c_matrix(to_fill_in)
        self._converted_distance=None
    def __getitem__(self, key):
        return self._matrix[key]
    def __len__(self):
        return len(self._matrix)
    def out_distance(self, i):
        """The out-distance of a term i."""
        return self._matrix.rowsum(i)
    def in_distance(self, j):
        """The in-distance of a term j."""
        return self._matrix.colsum(j)
    def compute_converted_distance(self):
        """Calculate the converted distance, for the internal use of other 
        functions."""
        total=0.0
        for i in xrange(len(self)):
            total+=self.out_distance(i)
        self._converted_distance=total
    def relative_out_centrality(self, i):
        """Computes relative out centrality."""
        if self._converted_distance is None:
            self.compute_converted_distance()
        return self._converted_distance/float(self.out_distance(i))
    def relative_in_centrality(self, j):
        """Computes relative in centrality."""
        if self._converted_distance is None:
            self.compute_converted_distance()
        return self._converted_distance/float(self.in_distance(j))
    def max_centrality_norm_factor(self):
        """The normalization factor corresponding to the maximal centrality. 
        Used in the compactness calculation"""
        return float(len(self)**2 - len(self))*self._unreachable
    def min_centrality_norm_factor(self):
        """The normalization factor corresponding to the minimal centrality. 
        Used in the compactness calculation"""
        return float(len(self)**2 - len(self))
    def compactness(self):
        "Measures how connected the graph is"
        if self._converted_distance is None:
            self.compute_converted_distance()
        return (self.max_centrality_norm_factor()-self._converted_distance) \
                /(self.max_centrality_norm_factor()-
                    self.min_centrality_norm_factor())
    def stratum(self):
        "Measures the linearity of the graph"
        lap=(len(self)**3)/4.0 if len(self)%2==0 \
                               else (len(self)**3-len(self))/4.0
        total=0.0
        for i in xrange(len(self)):
            # We can't use the regular implementations, because we must
            # invalidate the unconnected nodes.
            status=0.0
            contrastatus=0.0
            for j in xrange(len(self)):
                rowval=self._matrix[i, j]
                colval=self._matrix[j, i]
                status+=0.0 if rowval==self._unreachable else rowval
                contrastatus+=0.0 if colval==self._unreachable else colval
            total+=abs(status-contrastatus)
        return total/lap
    