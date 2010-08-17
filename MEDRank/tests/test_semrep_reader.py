#!/usr/bin/env python
# encoding: utf-8
"""
test_semrep_reader.py

Tests the SEMREP reader and the graph builder by exercising them with actual 
data from MEDRank V1.

Created by Jorge Herskovic on 2008-05-13.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import sys
import os
from MEDRank.utility.logger import logging
import cPickle as pickle
import bz2
sys.path.append('../')
from file.chunkmap import chunkmap_factory
from file.semrep import SemrepOutput
from computation.graph_builder import SemrepGraphBuilder
from computation.pageranker import PageRanker
# import psyco; psyco.profile()
import time

def main():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s')
    chunkmap=chunkmap_factory(pickle.load(
                            bz2.BZ2File('test_data/5th.chunkmap.bz2')))
                            
    setupstart=time.clock()
    semrep_reader=SemrepOutput(bz2.BZ2File('test_data/5th.semrep.out.bz2'),
                                ["semrep wrapper error"],
                                chunkmap)
    semrep_grapher=SemrepGraphBuilder()
    pr_algorithm=PageRanker()
    count=0
    parsestart=time.clock()
    for article in semrep_reader:
        print "Read article", article.set_id,
        graph=semrep_grapher.create_graph(article.lines)
        print "graphed it",
        matrixed=graph.as_mapped_link_matrix()
        print "matrixed it,",
        fake_e_vector=[0.0] * len(matrixed)
        if fake_e_vector==[]:
            print "didn't pagerank because it was empty."
        else:
            ranked=pr_algorithm.evaluate(matrixed, fake_e_vector)
            print "pageranked it. Stats:", pr_algorithm.stats
        count+=1
    endparse=time.clock()   
    print "Total time elapsed: %1.3f seconds (%1.7f seconds were setup) for "\
          "%d total articles, for a grand total of %1.3f compressed "\
          "articles/second turned into semantic graphs, link matrices," \
          " and finally pageranked." % (
          endparse-setupstart, parsestart-setupstart, count, 
          float(count)/(endparse-setupstart))

if __name__ == '__main__':
    main()

