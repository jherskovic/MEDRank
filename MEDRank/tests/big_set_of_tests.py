#!/usr/bin/env python
# encoding: utf-8
"""
big_set_of_tests.py

Invokes unit tests for all modules. 
DO NOT EXECUTE TESTS WITH python -O - there are assertion tests that *WILL* fail.

Created by Jorge Herskovic on 2008-05-14.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import sys
import unittest
sys.path.append('../')
# Computation module
from computation.link_matrix import *
from computation.pageranker import *
from computation.weighted_pageranker import *
from computation.textranker import *
from computation.node import *
from computation.link import *
from computation.graph import *
from computation.graph_builder import *
from computation.mapped_link_matrix import *
from computation.mapped_ranker import *
from computation.semrep_graph_builder import *
from computation.metamap_cooccurrence_graph_builder import *
from computation.semrep_cooccurrence_graph_builder import *
# Evaluation module
from evaluation.evaluation import *
from evaluation.hoopers import *
from evaluation.precision import *
from evaluation.recall import *
from evaluation.savcc import *
from evaluation.savcc_matrix import *
from evaluation.savcc_normalized_matrix import *
from evaluation.vocabulary_vector import *
from evaluation.result import *
from evaluation.result_set import *
from evaluation.group import *
from evaluation.common import *
# file
from file.chunkmap import *
from file.disk_backed_dict import *
from file.metamap import *
from file.nlm_output import *
from file.semrep import *
from file.text import *
from file.mti import *
# mesh
from mesh.term import *
from mesh.tree import *
from mesh.tree_node import *
from mesh.expression import *
# pubmed
from pubmed.pmid import *
# umls
from umls.concept import *
from umls.concrete_concept import *
from umls.names_and_ids import *
from umls.converter import *
# Workflow
from utility.workflow import *
def main():
    unittest.main()

if __name__ == '__main__':
    main()

