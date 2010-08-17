#!/usr/bin/env python
# encoding: utf-8
"""
vocabulary_vector.py

Created by Jorge Herskovic on 2008-04-10.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

from MEDRank.utility.logger import logging, ULTRADEBUG
import math

class VocabularyVector(object):
    """A sparse vector that represents a phrase or utterance in some
    vocabulary."""
    __slots__=['__max_size', '__store']
    def __init__(self, vocabulary_size):
        logging.log(ULTRADEBUG, "Creating vocabulary_vector of size %d",
                      vocabulary_size)
        self.__max_size=vocabulary_size
        self.__store={}
    def __setitem__(self, key, value):
        assert type(key) is int
        # Enable negative vector sizes like native python lists
        if key<0:
            key=self.__max_size+key
        assert key>=0 and key<self.__max_size
        # If the new value is 0, we actually don't want the entry at all
        if value!=0.0:
            self.__store[key]=value
    def __getitem__(self, key):
        assert type(key) is int
        # Enable negative vector sizes like native python lists
        if key<0:
            key=self.__max_size+key
        assert key>=0 and key<self.__max_size
        return self.__store.get(key, 0.0)
    def nonzero(self):
        """Returns the positions for which the vector is not zero."""
        notzero=self.__store.keys()
        notzero.sort()
        return notzero
    def __repr__(self):
        return "<%d element vocabulary_vector at %#x>" % (self.__max_size,
                                                         id(self))
    def as_list(self):
        """Represents the vector as a non-sparse python list"""
        vector_list=[0.0] * self.__max_size
        for k, value in self.__store.iteritems():
            vector_list[k]=value
        return vector_list
    def __len__(self):
        return self.__max_size
    def length(self):
        """Returns the vector's length (its modulus, not its
        dimensionality!)"""
        accum=0.0
        for value in self.__store.itervalues():
            accum+=value*value
        return math.sqrt(accum)
    # pylint: disable-msg=W0212
    def __add__(self, other):
        """Adds two vocabulary_vectors together."""
        # Sanity check - the vectors must be the same size
        assert self.__max_size==other.__max_size
        #    raise TypeError("The two vectors are different sizes!")
        result=VocabularyVector(self.__max_size)
        # Merge the two lists of keys together
        keys_to_be_added=set(self.__store.keys()) | set(other.__store.keys())
        for k in keys_to_be_added:
            result[k]=self[k]+other[k]
        return result
    def dot(self, other):
        """Implements the dot product between two vocabulary vectors."""
        # Sanity check - the vectors must be the same size
        assert self.__max_size==other.__max_size
        #    raise TypeError("The two vectors are different sizes!")
        result=0.0
        # Merge the two lists of keys together
        keys_to_be_dotted=set(self.__store.keys()) | set(other.__store.keys())
        for k in keys_to_be_dotted:
            result+=self[k]*other[k]
        return result
    def scale(self, scalar):
        """Multiplies all terms by a scalar, returning a new scaled vector"""
        result=VocabularyVector(self.__max_size)
        for k, value in self.__store.iteritems():
            result[k]=value*scalar
        return result
