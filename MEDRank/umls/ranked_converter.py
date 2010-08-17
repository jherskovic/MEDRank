#!/usr/bin/env python
# encoding: utf-8
"""
ranked_converter.py

Takes a converter instance and wraps it to return scored converted terms,
using the RankerResultSet class to return results. It will release all results
upon calling the end_conversion()  method. 

Created by Jorge Herskovic on 2008-05-23.
Copyright (c) 2008 University of Texas - Houston. All rights reserved.
"""
# Disable warnings about spaces before operators (they drive me crazy)
# pylint: disable-msg=C0322

# Don't complain about as_ExpressionList
# pylint: disable-msg=C0103
from MEDRank.utility.logger import logging, ULTRADEBUG
from MEDRank.umls.concept import Concept
from MEDRank.mesh.expression import ExpressionList

class RankedConversionResult(object):
    """Holds a converted set of terms and their scores. Add terms and scores
    with the add_term_score() method. Please don't add terms while iterating;
    you won't see them (since the iteration is in order).
    """
    def __init__(self):
        self._scores=[]
        self._terms=[]
    def add_term_score(self, term, score):
        """Add a term-score pair to the result set."""
        self._terms.append(term)
        self._scores.append(score)
    def end_conversion(self):
        """Ends the conversion, preparing the terms and scores for later use"""
        _scored_pairs=zip(self._scores, self._terms)
        _scored_pairs.sort(reverse=True)
        self._scores=[x[0] for x in _scored_pairs]
        self._terms=[x[1] for x in _scored_pairs]
    def __iter__(self):
        _scored_pairs=zip(self._scores, self._terms)
        _scored_pairs.sort(reverse=True)
        for score, term in _scored_pairs:
            yield (term, score)
        return
    def __len__(self):
        return len(self._scores)
    def terms_higher_than_or_equal_to(self, bottom_score):
        """Returns an expression list with just the terms over a certain
        score."""
        new_results=RankedConversionResult()
        for term, score in self:
            if score>=bottom_score:
                new_results.add_term_score(term, score)
        return new_results
    def as_ExpressionList(self):
        "Returns an ExpressionList containing the results of the conversion"
        return ExpressionList([x[0] for x in self])
    def __repr__(self):
        zipped=zip(self._scores, self._terms)
        zipped.sort(reverse=True)
        return "<RankedConversionResult @ %#x: %r>" % (id(self),
                                                       zipped)
class RankedConverter(object):
    """The RankedConverter will drive a Converter instance and return
    RankedConversionResult. It will also by default
    boost the score of added checktags.
    
    Call convert to request conversion of a RankedResultSet."""
    def __init__(self, converter, checktag_boost_score=0.5):
        self._my_converter=converter
        self._checktag_boost=checktag_boost_score
    def __repr__(self):
        return "<%s wrapping %r>" % (self.__class__.__name__, 
                                     self._my_converter)
    def convert(self, a_ranked_result_set):
        """Convert a ranked result set into a RankedConversionResult.
        In other words, convert a ranked term list to its MeSH equivalents."""
        result=RankedConversionResult()
        self._my_converter.start_conversion()
        for incoming_term, incoming_score in a_ranked_result_set:
            converted=self._my_converter.convert(
                        Concept(incoming_term.node_id))
            if converted.utterance!=[]:
                result.add_term_score(converted, incoming_score)
            converted=self._my_converter.end_conversion()
            if converted.utterance!=[]:
                result.add_term_score(converted, incoming_score+
                                                 self._checktag_boost)
        logging.log(ULTRADEBUG, "RankedConverter results: %r", result)
        return result
    # Expose data
    def get_data(self):
        """Expose the inner converter's data for other uses."""
        return self._my_converter.data
    data=property(get_data)
