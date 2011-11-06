#!/usr/bin/env python
# encoding: utf-8
"""
base_matrix.py

Maps the numpy matrix type to the MEDRank type hierarchy

Created by Jorge Herskovic on 2008-06-19.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import numpy
# Disable warnings about spaces before operators (they drive me crazy)
# pylint: disable-msg=C0322

# Ignore message about unused loop variable in the constructor of Matrix 
# pylint: disable-msg=W0612

class Matrix(numpy.matrix):
    # Implement a few traditional MEDRank matrix methods for easier porting
    normalize=lambda x: x/x.max()
    rowsum=lambda x, i: x[i].sum()
    colsum=lambda x, j: x.T[j].sum()
    row_nonzero=lambda m, i: len([1 for x in range(m[i].size) if m[i, x] != 0.0])
    col_nonzero=lambda m, j: Matrix.row_nonzero(m.T, j)
