#!/usr/bin/env python
# encoding: utf-8
"""
hoopers.py

Created by Jorge Herskovic on 2008-04-09.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

from MEDRank.utility.logger import logging
from MEDRank.evaluation.evaluation import Evaluation
from MEDRank.evaluation.result import Result

class HoopersResult(Result):
    """Represents the result of a Hooper's IC"""
    pass
    
class Hoopers(Evaluation):
    """Implements a Hooper's IC evaluator. Hooper's IC is defined as:
                  A
        IC=-------------
              A + M + N

    Where A is the number of terms in common, M is the number of terms used
    by indexer M but not N, and viceversa.
    """
    _my_result_class=HoopersResult
    def _evaluate(self, term_list_1, term_list_2):
        "Compute Hooper's IC between two lists of terms."
        logging.debug("""Evaluating Hooper's IC with term_list_1=%s and
        term_list_2=%s""", term_list_1, term_list_2)
        terms_in_common=[]
        length_list_1=len(term_list_1)
        # Keep this number separate, because it will change!
        original_len_list_1=length_list_1
        length_list_2=len(term_list_2)
        for i in xrange(original_len_list_1):
            term=term_list_1[i]
            if term in term_list_2:
                terms_in_common.append(term)
                length_list_1=length_list_1-1
                length_list_2=length_list_2-1
        # Compute A and return the result
        common=len(terms_in_common)
        logging.debug("No terms in common, returning 0")
        if common==0: 
            return 0.0

        return float(common)/(common+length_list_1+length_list_2)
