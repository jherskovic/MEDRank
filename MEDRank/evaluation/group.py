#!/usr/bin/env python
# encoding: utf-8
"""
group.py

Represents a group of evaluations that returns a set of results. Evaluations
shouldn't be called directly (except in very specific cases); they should be 
called as part of a group of evaluations.

Created by Jorge Herskovic on 2008-05-15.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

from MEDRank.utility.logger import logging, ULTRADEBUG
from MEDRank.evaluation.result_set import ResultSet

class EvaluationGroup(set):
    """Represents a set of evaluators that returns a set of results.
    An EvaluationGroup is also (in a twisted sense) a kind of evaluator, so
    it inherits from Evaluation."""
    def evaluate(self, term_list_1, term_list_2):
        """Performs a set of evaluations (in no particular order) and
        returns their results as members of a ResultSet"""
        results=ResultSet()
        for each_evaluator in self:
            logging.log(ULTRADEBUG, "Applying %s as part of an EvaluationGroup", 
                          each_evaluator.__class__.__name__)
            results.add(each_evaluator.evaluate(term_list_1, term_list_2))
        return results
    def test_names(self):
        """Returns the names of the tests in the evaluator."""
        return set([x.test_name() for x in self])
    def __repr__(self):
        return "<EvaluationGroup: %r>" % list(self.test_names())

