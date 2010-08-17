#!/usr/bin/env python
# encoding: utf-8
"""
savcc.py

Created by Jorge Herskovic on 2008-04-21.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

from MEDRank.utility.logger import logging, ULTRADEBUG
from MEDRank.evaluation.evaluation import Evaluation
from MEDRank.evaluation.result import Result

class SavccResult(Result):
    """Represents the result of a SAVCC evaluation"""
    pass

class Savcc(Evaluation):
    """Implements an evaluator that computes the Semantically Aware Vector
    Cosine Comparison between two lists of terms.

                      I1[(alpha*I2)+(1-alpha x M)I2]
    SAVCC(I1, I2) = ------------------------
                    |I1||[(alpha*I2)+(1-alpha x M)I2]|
                        
    This code WILL NOT WORK RIGHT NOW BECAUSE IT REQUIRES TREE TO BE
    IMPLEMENTED. The implementation assumes that the tree will have a method
    to build term vectors called term_vector that returns vocabulary_vectors.
    """
    _my_result_class=SavccResult
    def __init__(self, parameters):
        Evaluation.__init__(self, parameters)
        self._my_matrix=self._parameters.savcc_matrix
        self._alpha=self._parameters.alpha
        self._my_tree=self._parameters.mesh_tree
        logging.debug("Creating SAVCC evaluator. Tree %r Alpha %1.5f "
                      "Matrix %r", self._my_tree, self._alpha, 
                                   self._my_matrix)
    def _evaluate(self, gold_standard, seen_terms):
        "Compute SAVCC between two sets of terms"
        logging.debug('Gold standard=%s Seen terms=%s alpha=%1.5f',
                      gold_standard,
                      seen_terms,
                      self._alpha)
        gold_standard_vector=self._my_tree.term_vector(gold_standard)
        seen_vector=self._my_tree.term_vector(seen_terms)
        # This computes [(alpha*I2)+(1-alpha x M)I2]
        modified_term=seen_vector.scale(self._alpha)+\
            self._my_matrix.mult_by_vector(seen_vector).scale(1-self._alpha)
        logging.log(ULTRADEBUG, "Modified term=%r", modified_term)
        # I1 * modified_term
        numerator=gold_standard_vector.dot(modified_term)
        # Denominator of the whole thing
        denominator=gold_standard_vector.length()*modified_term.length()
        try:
            result=numerator/denominator
        except ZeroDivisionError:
            logging.warn("ZeroDivisionError when computing SAVCC for %r and %r:",
                     gold_standard, seen_terms)
            result=0
        logging.log(ULTRADEBUG, "Numerator=%1.7f Denominator=%1.7f Result=%1.7f",
                      numerator,
                      denominator,
                      result)
        return result
