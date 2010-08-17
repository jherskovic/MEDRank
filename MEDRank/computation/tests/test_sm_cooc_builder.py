#!/usr/bin/env python
# encoding: utf-8
"""
test_sm_cooc_builder.py

Created by Jorge Herskovic on 2008-05-29.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import unittest
from MEDRank.computation.semrep_cooccurrence_graph_builder import *
from MEDRank.file.semrep import (EntityLine, RelationLine)

class semrep_cooccurrence_graph_builderTests(unittest.TestCase):
    def setUp(self):
        # Test setup borrowed from semrep.py
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
        # Metamap test from metamap.py

    def testSemrepCooccurrenceGraphBuilder(self):
        my_builder=SemrepCooccurrenceGraphBuilder()
        graph=my_builder.create_graph([x for x in self.sro][0].lines)
        # There were 2 concepts in the original file; there should be
        # 1 relationship in this graph. The relationship should be between
        # the two original entities
        self.assertEqual(1, len(graph._relationships))
        rels=[x for x in graph._relationships]
        self.assertEqual('c0392760', rels[0].node1.node_id)
        self.assertEqual('c1314939', rels[0].node2.node_id)


if __name__ == '__main__':
    unittest.main()