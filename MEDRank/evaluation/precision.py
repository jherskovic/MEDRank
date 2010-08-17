#!/usr/bin/env python
# encoding: utf-8
"""
precision.py

Created by Jorge Herskovic on 2008-04-09.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

from MEDRank.utility.logger import logging
from MEDRank.evaluation.evaluation import Evaluation
from MEDRank.evaluation.result import Result

class PrecisionResult(Result):
    """Represents the result of a Precision evaluation"""
    pass
    
class Precision(Evaluation):
    """Implements an evaluator that computes precision between two lists.
    The first one should be the gold standard, the second the terms to 
    evaluate."""
    _my_result_class=PrecisionResult
    def _evaluate(self, gold_standard, seen_terms):
        "Compute precision."
        logging.debug("Computing precision between gold standard %r and "
                      "term list %r", gold_standard, seen_terms)
        correct_terms=[x for x in seen_terms if x in gold_standard]
        size_seen_terms=len(seen_terms)
        size_correct_terms=len(correct_terms)

        return float(size_correct_terms)/size_seen_terms
