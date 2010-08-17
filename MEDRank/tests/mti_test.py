#!/usr/bin/env python
# encoding: utf-8
"""
mti_test.py

Created by Jorge Herskovic on 2008-05-27.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import sys
import os
from MEDRank.utility.logger import logging
import cPickle as pickle
import bz2
from MEDRank.file.chunkmap import chunkmap_factory
from MEDRank.file.disk_backed_dict import StringDBDict
from MEDRank.file.mti import (MtiOutput, DEFAULT_LINES_TO_IGNORE)
from MEDRank.umls.concept import Concept
from MEDRank.computation.semrep_cooccurrence_graph_builder \
    import SemrepCooccurrenceGraphBuilder
from MEDRank.computation.node import Node
from MEDRank.computation.textranker import TextRanker
from MEDRank.evaluation.evaluation import EvaluationParameters
# impMEDRank.ort psyco; psyco.profile()
from MEDRank.utility.workflow import Workflow
import math
import time
import csv

class MtiWorkflow(Workflow):
    def graph_and_rank(self, article):
        """Uses the information from the MTI file to simulate graphing and
        ranking. Returns a set of (Node, score) tuples that a 
        RankedConverter can use."""
        this_article=[]
        for l in article.lines:
            this_article.append((Node(l.CUI, l.description, l.confidence),
                                 l.confidence))
        return this_article
    
SAVCC_MATRIX_FILE=\
 '/Users/jherskovic/Projects/MEDRank/MeSH_matrix/complete_distance_matrix.bin'
MESH_TREE_FILE='../../data/mesh07_data.db'
UMLS_CONVERTER_DATA='../../data/mti_converter_data.p'
UMLS_CONCEPT_DATA='../../data/umls_concepts.db'
PAGERANK_CUTOFF=0.12
OUTPUT_FILE='mti_just_abstracts_results.csv'

def main():
    my_format_string='%(asctime)s %(levelname)s %(module)s.' \
                      '%(funcName)s: %(message)s'
    logging.basicConfig(level=logging.DEBUG,
                        format=my_format_string)
    chunkmap=chunkmap_factory(pickle.load(
                    bz2.BZ2File('test_data/all_abstracts.mti_chunkmap.bz2')))
                            
    reader=MtiOutput(bz2.BZ2File('test_data/all_abstracts.mti.just_metamap.out.bz2'),
                                DEFAULT_LINES_TO_IGNORE,
                                chunkmap)
    eval_params=EvaluationParameters()
    eval_params.alpha=0.65
    work=MtiWorkflow(reader, None, None, eval_params,
                  PAGERANK_CUTOFF, MESH_TREE_FILE, SAVCC_MATRIX_FILE,
                  lambda x: 1.0/math.exp(x) if x>=0 and x<5 else 0.0,
                  UMLS_CONVERTER_DATA, UMLS_CONCEPT_DATA,
                  open(OUTPUT_FILE, 'w'))
    work.run()


if __name__ == '__main__':
    main()

