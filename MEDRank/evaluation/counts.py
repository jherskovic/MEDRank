#!/usr/bin/env python
# encoding: utf-8
"""
counts.py

Created by Jorge Herskovic on 2008-05-22.
Copyright (c) 2008 University of Texas - Houston. All rights reserved.
"""

from MEDRank.evaluation.evaluation import (Evaluation)
from MEDRank.evaluation.result import Result

class GoldStandardCountResult(Result):
    """Represents the Count of terms in the gold standard"""
    pass
    
class GoldStandardCount(Evaluation):
    """Counts the number of terms in the Gold Standard"""
    _my_result_class=GoldStandardCountResult
    def _evaluate(self, gold_standard, seen_terms):
        "Counts the number of terms in the gold standard"
        return len(gold_standard)

class SeenCountResult(Result):
    """Represents the Count of terms in the Seen list"""
    pass

class SeenCount(Evaluation):
    """Counts the number of terms in the Seen terms"""
    _my_result_class=SeenCountResult
    def _evaluate(self, gold_standard, seen_terms):
        "Perform the actual count"
        return len(seen_terms)
        
