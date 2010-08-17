#!/usr/bin/env python
# encoding: utf-8
"""
test_metamap_reader.py

Exercises the METAMAP reader and graph builders with actual data.

Created by Jorge Herskovic on 2008-05-14.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import sys
sys.setcheckinterval(10000)
import gc
#gc_thresholds=gc.get_threshold()
#gc.set_threshold(gc_thresholds[0]*10, gc_thresholds[1]*5, gc_thresholds[2]*3)
#gc.set_debug(gc.DEBUG_STATS)
#import psyco; psyco.profile(50)
import os
import cPickle as pickle
from MEDRank.utility.logger import logging
import bz2
sys.path.append('../')
from file.chunkmap import chunkmap_factory
from file.metamap import (MetamapOutput, DEFAULT_LINES_TO_IGNORE)
from computation.graph_builder import MetamapCoccurrenceGraphBuilder
from computation.pageranker import PageRanker
from computation.mapped_ranker import MappedRanker
from computation.textranker import TextRanker
import time
#import psyco; psyco.profile(0.5)

def main():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s')
    chunkmap=chunkmap_factory(pickle.load(
                            bz2.BZ2File(
                            'test_data/metamap.chunkmap.bz2')))
                            
    setupstart=time.clock()
    metamap_reader=MetamapOutput(bz2.BZ2File(
                                'test_data/metamap.out.bz2'),
                                DEFAULT_LINES_TO_IGNORE,
                                chunkmap)
    grapher=MetamapCoccurrenceGraphBuilder()
    # PageRank is not the correct algorithm for a matrix of adirectional nodes
    # but it'll do for now, to exercise the system
    # pr_algorithm=PageRanker()
    # TextRanker now written
    pr_algorithm=MappedRanker(TextRanker())
    count=0
    parsestart=time.clock()
    for article in metamap_reader:
        print "Read article", article.set_id,
        graph=grapher.create_graph(article.lines)
        print "graphed it",
        matrix=graph.as_mapped_link_matrix()
        print "turned it into a", matrix, 
        #fake_e_vector=[0.0] * len(matrix)
        if len(matrix)==0:
            print "didn't pagerank because it was empty."
        else:
            ranked=pr_algorithm.evaluate(matrix)
            print "TextRanked it. First results: %r Stats:" % \
                    [x for x in ranked][:5],  pr_algorithm.stats
        count+=1
    endparse=time.clock()   
    print "Total time elapsed: %1.3f seconds (%1.7f seconds were setup) "\
          "for %d total articles, for a grand total of %1.3f compressed "\
          "articles/second read, turned into link matrices, and " \
          " pageranked." \
          % (endparse-setupstart, parsestart-setupstart, count, 
             float(count)/(endparse-setupstart))
    
    count+=1

if __name__ == '__main__':
    main()

