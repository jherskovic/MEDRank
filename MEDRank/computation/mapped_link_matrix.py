#!/usr/bin/env python
# encoding: utf-8
"""
mapped_link_matrix.py

Created by Jorge Herskovic on 2008-05-16.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

from MEDRank.computation.link_matrix import LinkMatrix
from numpy import zeros

class MappedLinkMatrix(LinkMatrix):
    """Represents a link matrix that keeps an association with a vocabulary.
    Instead of number of terms, the matrix receives the set of items to
    associate with matrix rows and mantains the association internally.
    
    The term set must have an iterator."""        
    def get_term_position(self, a_term):
        """Returns the index position that corresponds to a certain term."""
        return self._term_set.index(a_term)
    # The terms property.
    def terms_fget(self):
        "Getter for the terms property"
        return self._term_set
    def terms_fset(self, terms):
        assert isinstance(terms, list)
        self._term_set=terms
    terms=property(terms_fget, terms_fset)
    
