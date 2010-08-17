#!/usr/bin/env python
# encoding: utf-8
"""
f2.py

Created by Jorge Herskovic on 2008-12-02.
Copyright (c) 2008 University of Texas - Houston. All rights reserved.
"""

from MEDRank.utility.logger import logging
from MEDRank.evaluation.evaluation import Evaluation
from MEDRank.evaluation.result import Result
from MEDRank.evaluation.recall import Recall
from MEDRank.evaluation.precision import Precision

class F2Result(Result):
    """Represents the result of an F2 computation"""
    pass
    
class F2(Evaluation):
    _my_result_class=F2Result
    def _evaluate(self, gold_standard, seen_terms):
        "Compute the actual F2."
        logging.debug("Computing F2 between gold standard %r and "
                      "term list %r", gold_standard, seen_terms)
        r=Recall().evaluate(gold_standard, seen_terms).result
        p=Precision().evaluate(gold_standard, seen_terms).result
        if r==0.0 and p==0.0:
            return 0.0
        return (5.0*r*p)/(4.0*p+r)
