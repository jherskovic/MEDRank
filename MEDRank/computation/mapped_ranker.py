#!/usr/bin/env python
# encoding: utf-8
"""
mapped_ranker.py

Describes and encapsulates how to run a ranker and obtain a set of term->score
results.

Created by Jorge Herskovic on 2008-05-20.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

from MEDRank.computation.pageranker import PageRanker
from MEDRank.computation.mapped_link_matrix import MappedLinkMatrix

class RankerResultSet(object):
    """Describes a set of ranking results as sorted term->score pairings.
    Please iterate through the RankerResultSet to use it."""
    def __init__(self, original_mapped_matrix, ranking_scores):
        # Sanity check
        if len(original_mapped_matrix.terms)!=len(ranking_scores):
            raise ValueError("The mapped matrix does not have the same"
                             "number of terms (%d) as the set of scores (%d)"
                             % (len(original_mapped_matrix.terms),
                                len(ranking_scores)))
        self._scored_terms=zip(ranking_scores, original_mapped_matrix.terms)
        self._scored_terms.sort(reverse=True)
    def __getitem__(self, key):
        # The preferred access route for this result set is the iterator
        termkey=[x[1] for x in self._scored_terms].index(key)
        return self._scored_terms[termkey][0]
    def __iter__(self):
        """The default iterator works on keys and values"""
        for score, term in self._scored_terms:
            yield (term, score)
        return
    def __repr__(self):
        return "<%s: %r>" % (self.__class__.__name__, self._scored_terms)
    
class MappedRanker(object):
    """Wraps a Ranker so that it returns a RankerResultSet, that always pairs
    terms with their scores correctly."""
    def __init__(self, ranker):
        self._my_ranker=ranker
    def evaluate(self, matrix, *other_args):
        """Run the ranker and return the result as a RankerResultSet."""
        scores=self._my_ranker.evaluate(matrix, *other_args)
        result=RankerResultSet(matrix, scores)
        return result
    def __repr__(self):
        return "<%s for %r>" % (self.__class__.__name__, self._my_ranker)
    def __getattr__(self, attr):
        # Pass through to the wrapped ranker
        return self._my_ranker.__getattribute__(attr)
