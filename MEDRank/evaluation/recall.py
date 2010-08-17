#!/usr/bin/env python
# encoding: utf-8
"""
recall.py

Created by Jorge Herskovic on 2008-04-09.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

from MEDRank.utility.logger import logging
from MEDRank.evaluation.evaluation import Evaluation
from MEDRank.evaluation.result import Result

class RecallResult(Result):
    """Represents the result of a Recall evaluation"""
    pass
    
class TotalRecallResult(Result):
    """Represents the result of a TotalRecall evaluation."""
    pass
    
class Recall(Evaluation):
    """Implements an evaluator that computes recall."""
    _my_result_class=RecallResult
    def _evaluate(self, gold_standard, seen_terms):
        "Compute the actual recall."
        logging.debug("Computing recall between gold standard %r and "
                      "term list %r", gold_standard, seen_terms)
        correct_terms=[x for x in seen_terms if x in gold_standard]
        size_gold_standard=len(gold_standard)
        size_correct_terms=len(correct_terms)

        return float(size_correct_terms)/size_gold_standard

class TotalRecall(Recall):
    """Another name for recall, to use for outputting the Total Recall of
    articles."""
    _my_result_class=TotalRecallResult
    