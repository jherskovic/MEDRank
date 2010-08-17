#!/usr/bin/env python
# encoding: utf-8
"""
sample_full_processing_workflow.py

Created by Jorge Herskovic on 2008-05-21.
Copyright (c) 2008 University of Texas - Houston. All rights reserved.
"""

import sys
import getopt


help_message = '''
The help message goes here.
'''

import sys
import os
from MEDRank.utility.logger import logging
import cPickle as pickle
import bz2
from MEDRank.file.chunkmap import chunkmap_factory
from MEDRank.file.disk_backed_dict import StringDBDict
from MEDRank.file.semrep import (SemrepOutput, DEFAULT_LINES_TO_IGNORE)
from MEDRank.computation.semrep_cooccurrence_graph_builder \
    import SemrepCooccurrenceGraphBuilder
from MEDRank.computation.textranker import TextRanker
from MEDRank.evaluation.evaluation import EvaluationParameters
from MEDRank.utility.workflow import Workflow
from MEDRank.umls.ranked_converter import RankedConversionResult
from MEDRank.computation.tf_idf import TF_IDF

import math
import time
import csv

SAVCC_MATRIX_FILE=\
 '/Users/jherskovic/Projects/MEDRank/MeSH_matrix/complete_distance_matrix.bin'
MESH_TREE_FILE='../../data/mesh07_data.db'
UMLS_CONVERTER_DATA='../../data/mti_converter_data.p'
UMLS_CONCEPT_DATA='../../data/umls_concepts.db'
PAGERANK_CUTOFF=0.125
OUTPUT_FILE='super_duper_results_tfidf_max_20_with_c.csv'

class myWorkflow(Workflow):
    def flatten_generated_terms(self, gstd, gen):
        fake_converted=RankedConversionResult()
        #count=len(gstd)
        count=20
        for t, s in gen:
            fake_converted.add_term_score(t, s)
            if len(fake_converted.as_ExpressionList().flatten())>=count:
                break
        return fake_converted.as_ExpressionList().flatten()
    
def main():
    my_format_string='%(asctime)s %(levelname)s %(module)s.' \
                      '%(funcName)s: %(message)s'
    logging.basicConfig(level=logging.INFO,
                        format=my_format_string)
    chunkmap=chunkmap_factory(pickle.load(
                            bz2.BZ2File('test_data/5th.chunkmap.bz2')))
                            
    semrep_reader=SemrepOutput(bz2.BZ2File('test_data/5th.semrep.out.bz2'),
                                DEFAULT_LINES_TO_IGNORE,
                                chunkmap)
    tfidf=TF_IDF(file_mode="c")
    tfidf.build_tf_from_file(semrep_reader)
    semrep_reader.rewind()

    semrep_grapher=SemrepCooccurrenceGraphBuilder(node_weight_threshold=0.001,
                                                  link_weight_threshold=0.003,
                                                  tf_idf_provider=tfidf
                                                  )
    eval_params=EvaluationParameters()
    eval_params.alpha=0.65
    work=myWorkflow(semrep_reader, semrep_grapher, TextRanker(), eval_params,
                  PAGERANK_CUTOFF, MESH_TREE_FILE, SAVCC_MATRIX_FILE,
                  lambda x: 1.0/math.exp(x) if x>=0 and x<5 else 0.0,
                  UMLS_CONVERTER_DATA, UMLS_CONCEPT_DATA,
                  open(OUTPUT_FILE, 'w'))
    work.run()
    
if __name__ == '__main__':
    main()
