#!/usr/bin/env python
# encoding: utf-8
"""
common.py

Defines some common evaluation groups.

Created by Jorge Herskovic on 2008-05-15.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

from MEDRank.evaluation.hoopers import Hoopers
from MEDRank.evaluation.precision import Precision
from MEDRank.evaluation.recall import Recall
from MEDRank.evaluation.f2 import F2
from MEDRank.evaluation.savcc import Savcc
from MEDRank.evaluation.group import EvaluationGroup
from MEDRank.evaluation.counts import (GoldStandardCount, SeenCount)

def quick(parameter_set):
    """Creates a quick EvaluationGroup - performs all evaluations except 
    Savcc."""
    return EvaluationGroup([Hoopers(parameter_set),
                            Precision(parameter_set), 
                            Recall(parameter_set),
                            GoldStandardCount(parameter_set),
                            SeenCount(parameter_set),
                            F2(parameter_set),
                            ])

def comprehensive(parameter_set):
    """Creates a comprehensive EvaluationGroup that performs all of the 
    known evaluations. It is the quick evaluation group, plus Savcc."""
    return quick(parameter_set) | EvaluationGroup([Savcc(parameter_set)])

