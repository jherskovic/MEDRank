#!/usr/bin/env python
# encoding: utf-8
"""
base_matrix.py

Represents a generic matrix, with some common operations.

Created by Jorge Herskovic on 2008-06-19.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import operator
from MEDRank.utility.logger import logging
# Disable warnings about spaces before operators (they drive me crazy)
# pylint: disable-msg=C0322

# Ignore message about unused loop variable in the constructor of Matrix 
# pylint: disable-msg=W0612

class Matrix(object):
    """Represents a generic matrix."""
    def __init__(self, matrix_size):
        self.__n=matrix_size
        one_row=[0] * self.__n
        # Append a new copy of each row for self.__n times
        self.__m=[one_row[:] for i in xrange(self.__n)]
        return
    def __len__(self):
        return self.__n
    def __getitem__(self, key):
        i, j=key
        return self.__m[i][j]
    def __setitem__(self, key, value):
        i, j=key
        self.__m[i][j]=value
    def __repr__(self):
        return "<%dx%d %s>" % (self.__n, self.__n, self.__class__.__name__)
    def __eq__(self, other):
        """SLOW comparison operation!"""
        if len(self)!=len(other):
            return False
        for i in xrange(len(self)):
            for j in xrange(len(self)):
                if self[i, j]!=other[i, j]:
                    logging.debug("FAIL @%d, %d. Self=%r, other=%r", 
                                  i, j, self[i,j], other[i,j])
                    return False
        return True
    def rowsum(self, i):
        """Returns the sum of a matrix row"""
        return reduce(operator.add, self.__m[i])
    def colsum(self, j):
        """Returns the sum of a matrix column"""
        return reduce(operator.add, (x[j] for x in self.__m))
    def row_nonzero(self, i):
        """Returns the number of nonzero elements in a matrix row"""
        return reduce(operator.add, (1 if x!=0.0 else 0 for x in self.__m[i]))
    def col_nonzero(self, j):
        """Returns the number of nonzero elements in a matrix column"""
        return reduce(operator.add, (1 if x!=0.0 else 0 for x in
                                       (y[j] for y in self.__m)))
    def get_row(self, i):
        """Returns a single matrix row as a list."""
        return self.__m[i]
    def set_row(self, i, row):
        """Sets an entire matrix row at once."""
        self.__m[i]=row
    def max(self):
        """Returns the single highest value in the entire matrix"""
        return reduce(max, (reduce(max, x) for x in self.__m))
    def iter_rows(self):
        """Iterator that works through rows, one at a time."""
        for i in xrange(len(self)):
            yield self.get_row(i)
        return
    def normalize(self, suggested_type=None):
        """Returns a normalized version of the matrix. Does not modify the
        matrix in place (that's unpythonic!)"""
        # This may fail if everything's 0, but I want it to fail loudly, not
        # do something "clever"
        if suggested_type is None:
            suggested_type=Matrix
        my_max=float(self.max()) # Unfortunately Python will not cast
                                 # implicitly when dividing
        result=suggested_type(len(self)) # Build a new instance of whatever
                                        # descendant actually invoked this.
        for i in xrange(len(self)):
            new_row=[0.0] * len(self)
            this_row=self.get_row(i)
            for j in xrange(len(self)):
                new_row[j]=this_row[j]/my_max
            result.set_row(i, new_row)
        return result
    def transpose(self, suggested_type=None):
        """Returns a transposed copy of the matrix. It is, unfortunately, a
        slow operation. It requires traversing the entire matrix..."""
        if suggested_type is None:
            suggested_type=Matrix
        transposed=suggested_type(len(self))
        for i in xrange(len(self)):
            # The i-th row of the new matrix must equal the i-th column of
            # the original one
            transposed.set_row(i, [x[i] for x in self.__m])
        return transposed
    def as_binary_c_matrix(self):
        """Returns a C array containing the matrix data. It will return one
        long, one-dimensional array with all the contents. C pointer magic 
        will be needed to use it reasonably.
        """
        import ctypes
        matrix_size=len(self)
        my_array_type=ctypes.c_int * (matrix_size**2)
        c_array=my_array_type()
        for i in xrange(matrix_size):
            for j in xrange(matrix_size):
                c_array[i*matrix_size+j]=int(self[i,j]>0)
        return c_array
    def fill_from_c_matrix(self, c_matrix):
        """Fills in data from a matrix handled by the C routines."""
        matrix_size=len(self)
        for i in xrange(matrix_size):
            for j in xrange(matrix_size):
                self[i, j]=int(c_matrix[i*matrix_size+j])
        return
