#!/usr/bin/env python
# encoding: utf-8
"""
test_semrep_graph_builder.py

Created by Jorge Herskovic on 2008-05-29.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import unittest
from MEDRank.computation.semrep_graph_builder import *
from MEDRank.computation.graph import Graph

class semrep_graph_builderTests(unittest.TestCase):
    def setUp(self):
        from MEDRank.file.semrep import (SemrepOutput)
        from MEDRank.file.metamap import (MetamapOutput)
        from MEDRank.file.chunkmap import chunkmap_factory
        import StringIO
        # logging.basicConfig(level=logging.DEBUG,
        #                  format='%(asctime)s %(levelname)s %(message)s')
        # This fakefile is NOT the same as semrep.py - this one has a 
        # relationship that should not be part of the graph, and one that 
        # should
        sr_file=StringIO.StringIO("SE|0000000000||ti|2|entity|Affecting|"
                                  "ftcn|C0392760|involved||||1000|319|326\n"
                                  "SE|0000000000||ti|2|entity|Involvement"
                                  "with|ftcn|C1314939|involved||"
                                  "||1000|319|326\n"
                                  "SE|0000000000||ti|2|relation|||Steroid"
                                  "hormone|horm,strd|horm|C0301818|"
                                  "||||||||901|115|130||INTERACTS_WITH"
                                  "||379|385|||steroid hormone"
                                  "receptor|gngm,aapp,rcpt|gngm|C0597519"
                                  "||None|steroid hormone receptors|their"
                                  " respective steroid hormone"
                                  " receptors|||||890|390|431\n"
                                  "SE|0000000000||ti|2|relation|||Affection"
                                  "|horm,strd|horm|C0392760|"
                                  "||||||||901|115|130||INTERACTS_WITH"
                                  "||379|385|||Involvement"
                                  "with|gngm,aapp,rcpt|gngm|C1314939"
                                  "||None|steroid hormone receptors|their"
                                  " respective steroid hormone"
                                  " receptors|||||890|390|431\n"
                                  "USELESS LINE!\n"
                                  "SE|0000000000||ti|3|text|Coactivator and"
                                  " corepressor proteins have recently been"
                                  " identified that interact with steroid"
                                  " hormone receptors and modulate"
                                  " transcriptional activation\n")
        fake_chunkmap=chunkmap_factory({'123.txt': [0]})
        self.sro=SemrepOutput(sr_file, ["USELESS LINE!"], fake_chunkmap)
    def testSemrepGraphBuilderBuildsGraphs(self):
        my_builder=SemrepGraphBuilder()
        articles=[x for x in self.sro]
        graphs=[my_builder.create_graph(x.lines) for x in articles]
        # The Graphs set should have one entity
        self.assertEqual(1, len(graphs))
        # The first element should be a graph
        self.assert_(type(graphs[0]) is Graph)
        # It should have a single relationship with two nodes
        matrix=graphs[0].as_mapped_link_matrix()
        self.assertEqual(len(matrix), 2)
    def testBuilderOnEmptySet(self):
        my_builder=SemrepGraphBuilder()
        graph=my_builder.create_graph([])
        self.assert_(type(graph) is Graph)

if __name__ == '__main__':
    unittest.main()