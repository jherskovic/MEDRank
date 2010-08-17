#!/usr/bin/env python
# encoding: utf-8
"""
savcc_matrix.py

Created by Jorge Herskovic on 2008-04-10.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

from MEDRank.utility.logger import logging, ULTRADEBUG
import struct
import os.path
import array
import sys
import cPickle
from MEDRank.evaluation.vocabulary_vector import VocabularyVector
from MEDRank.utility import cache

_DEFAULT_MATRIX_NAME=os.path.join(sys.exec_prefix, "medrank_data",
                                   "complete_distance_matrix_09.bin")

class SavccMatrix(object):
    """SavccMatrix is a very limited matrix class that actually stores
    semantic distances as bytes in a file. It converts them to closeness with
    a user-supplied lambda function at the moment of multiplication. It is
    written this way to save memory, because nothing else would fit in a
    32-bit machine and, actually, numpy is wasteful enough that a 64-bit
    machine w/4 GB of RAM wouldn't cut it, either. I just hope it's quick
    enough...
    
    This class is picklable so that it can be used with the multiprocessing
    module.
    
    I tried turning it into an mmapped file. It does not work faster.
    """
    def __init__(self, fileobject=None, transform_function=None):
        # The default matrix is installed together with the package
        if fileobject is None:
            fileobject=open(_DEFAULT_MATRIX_NAME, "rb")
        # The matrix file has a header that describes the size of the 
        # matrix in the first bytes
        self.header_size=struct.calcsize(">HH")
        # Read the file header and get the height and width of the matrix 
        self._height, self._width=struct.unpack('>HH',
                                      fileobject.read(self.header_size))
        logging.debug("We're reading a %dx%d matrix", self._height,
                                                      self._width)
        # Keep a link to the file. We'll need it.
        self._matrix_file=fileobject
        #self._matrix_file_handle=self._matrix_file.fileno()
        # This will store the mappings from bytes in the matrix to actual
        # results
        self.transform=[0.0]*256
        logging.log(ULTRADEBUG, "Building the transformation array.")
        for i in xrange(255):
            self.transform[i]=transform_function(i)
        # We leave the last value blank; it's always 0.
        logging.debug("The transformation array is %s.", str(self.transform))
        # Save the size of a byte for later
        self.byte_size=struct.calcsize('<B')
        self._cached_row=-1
        self._row_cache=None
    def __getstate__(self):
        return {'matrix': os.path.realpath(self._matrix_file.name),
                'h': self._height,
                'w': self._width,
                't': self.transform,
                'hs': self.header_size,
                'bs': self.byte_size}
    def __setstate__(self, state):
        self._matrix_file=open(state['matrix'], 'rb')
        self.header_size=state['hs']
        self.transform=state['t']
        self._height=state['h']
        self._width=state['w']
        self.byte_size=state['bs']
        self._cached_row=-1
        self._row_cache=None
    def __repr__(self):
        return "<%dx%d savcc_matrix residing in %s>" % (self._height,
                                                        self._width,
                                                    self._matrix_file.name)
    
    def _get_one_value(self, i, j):
        """Internal function that actually fetches a value from the disk
        array. Superceded by _get_value."""
        #if i<0 or i>=self._height or j<0 or j>=self._width:
        #    raise IndexError("""Dimensions out of range: the matrix is %dx%d
        #    but the requested element is %d,%d""", self._height,
        #                                           self._width, i, j)
        # Replaced the check with an assert so it can be optimized away if 
        # python is run with -O. It makes a big difference - there can be
        # hundreds of thousands of checks in a single multiplication
        assert i>=0 and i<self._height and j>=0 and j<self._width
        position=self.header_size+i*self._width+j
        self._matrix_file.seek(position, 0)
        a_byte=self._matrix_file.read(self.byte_size)
        # Use ord instead of struct to unpack the byte to avoid overhead
        ord_byte=ord(a_byte)
        # logging.debug("The byte at (%d,%d) is %d.", i, j, ord_byte)
        return self.transform[ord_byte]
    def _read_raw_row_from_disk(self, i):
        """Actually read a row from disk. PERFORMS NO SANITY CHECKS - DON'T
        USE THIS FUNCTION FROM OUTSIDE THE CLASS!!!"""
        position=self.header_size+i*self._width
        self._matrix_file.seek(position, 0)
        row=array.array('B', self._matrix_file.read(self._width))
        return row
    def _read_row_from_disk(self, i):
        return _read_raw_row_from_disk(i)
    def _get_value(self, i, j):
        """Internal function that returns one value from disk. Uses the row
        cache to avoid calling the OS if avoidable."""
        #if i<0 or i>=self._height or j<0 or j>=self._width:
        #    raise IndexError("""Dimensions out of range: the matrix is %dx%d
        #    but the requested element is %d,%d""", self._height,
        #                                           self._width, i, j)
        # Replaced the check with an assert so it can be optimized away if 
        # python is run with -O. It makes a big difference - there can be
        # hundreds of thousands of checks in a single multiplication
        assert i>=0 and i<self._height and j>=0 and j<self._width
        if self._cached_row!=i:
            # We don't cache the post-processed row, because we may not need
            # to convert every value. Most values will NOT be converted. 
            self._row_cache=self._read_raw_row_from_disk(i)
            self._cached_row=i
        return self.transform[self._row_cache[j]]
    def _get_row(self, i):
        """Convenience function for certain operations - reads an entire row
        at a time, avoiding lots of disk hits."""
        if i<0 or i>=self._height:
            raise IndexError("""Dimensions out of range: the matrix is %dx%d
            but the requested row is %d""", self._height, self._width, i)
        if self._cached_row!=i:
            # Avoid hits if it's the same row
            self._cached_row=i
            self._row_cache=self._read_raw_row_from_disk(i)
        return [self.transform[x] for x in self._row_cache]
        
    def __getitem__(self, key):
        i, j=key
        return self._get_value(i, j)
    def mult_by_vector(self, vector):
        """Multiplies the matrix by a vocabulary_vector, returning a new
        vocabulary_vector"""
        vec_size=len(vector)
        logging.log(ULTRADEBUG, "Multiplying by %s", vector)
        # Size checks
        if vec_size != self._width:
            raise ValueError("The vector and matrix shapes do not match.")
        result=VocabularyVector(self._height)
        # Operands to include in the multiplication
        nonzero_indices=vector.nonzero()
        for i in xrange(self._height):
            this_result=0.0
            for j in nonzero_indices:
                this_result+=self[i,j]*vector[j]
            result[i]=this_result
        return result
