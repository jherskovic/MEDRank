#!/usr/bin/env python
# encoding: utf-8
"""
evaluation.py

Created by Jorge Herskovic on 2008-04-09.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

from MEDRank.utility.logger import logging, ULTRADEBUG
from MEDRank.evaluation.result import Result

class EvaluationException(Exception):
    """An exception in the Evaluation class hierarchy."""
    pass

class EvaluationParameters(object):
    """A bag of parameters for the evaluators. This class should hold every
    parameter needed by an evaluator (just treat it like a dictionary)."""
    def __repr__(self):
        my_repr=[]
        for key, value in self.__dict__.iteritems():
            if key[:2]!='__':
                my_repr.append('%s=%r' % (key, value))
        return "<EvaluationParameters at %#x: %s>" % (id(self),
                                                      ', '.join(my_repr))
class Evaluation(object):
    """Base class for an evaluation function. Should not be instantiated
    directly. Accepts a link to a Parameters dictionary, which contains
    parameters that may (or may not) apply to every evaluation."""
    _my_result_class=Result
    def __init__(self, parameters=EvaluationParameters()):
        self._parameters=parameters
    def _evaluate(self, term_list_1, term_list_2):
        """Internal evaluation function - should be overridden to implement
        the actual evaluation"""
        pass
    def evaluate(self, term_list_1, term_list_2):
        if len(term_list_1)==0 or len(term_list_2)==0:
            logging.log(ULTRADEBUG, "%s tried to evaluate empty lists", 
                          self.__class__.__name__)
            return self._my_result_class(0.0)
        return self._my_result_class(self._evaluate(term_list_1, term_list_2))
    def test_name(self):
        return self.__class__.__name__
    def __repr__(self):
        return "<%s evaluator with %r parameters>" % (self.test_name, 
                                                      self._parameters)
