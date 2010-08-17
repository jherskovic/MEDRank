#!/usr/bin/env python
# encoding: utf-8
"""
test_mm_cooc_builder.py

Created by Jorge Herskovic on 2008-05-29.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""
import sys
import unittest
sys.path.append('../') # Necessary for testing
sys.path.append('../../')
from metamap_cooccurrence_graph_builder import *
from MEDRank.computation.graph import Graph

class metamap_cooccurrence_graph_builderTests(unittest.TestCase):
    def setUp(self):
        # Test setup borrowed from semrep.py
        from file.metamap import (MetamapOutput)
        from file.chunkmap import chunkmap_factory
        import StringIO
        # logging.basicConfig(level=logging.DEBUG,
        #                  format='%(asctime)s %(levelname)s %(message)s')
        # This fakefile is NOT the same as semrep.py - this one has a 
        # relationship that should not be part of the graph, and one that 
        # should
        # Metamap test from metamap.py
        mm_file=StringIO.StringIO("""
        >>>>> MMI
        * ERROR *
        0000000000|MM|530|Carboxyhemoglobin|C0007061| ["Carboxyhaemoglobin"-ti-1-"Carboxyhaemoglobin"]|TI
        0000000000|MM|223|Male population group|C0025266|["Men"-ti-1-"men"]|TI
        0000000000|MM|121|Levels|C0441889|["Levels"-ti-1-"levels"]|TI
        0000000000|MM|114|British|C0596227|["British"-ti-1-"British"]|TI
        0000000000|MM|114|Old|C0580836|["Old"-ti-1-"older"]|TI
        0000000000|MM|114|Old episode|C0677546|["Old"-ti-1-"older"]|TI
        <<<<< MMI
        >>>>> MMI
        0000000001|MM|585|Little's Disease|C0023882|["Little"-ti-1-"little"]|TI
        0000000001|MM|424|HAC protocol|C0062074|["HAD"-ti-1-"has"]|TI
        0000000001|MM|170|Background|C1706907|["Background"-ti-1-"BACKGROUND"]|TI
        0000000001|MM|170|General Population|C0683971|["General Population"-ti-1-"general population"]|TI
        0000000001|MM|170|Small|C0700321|["Little"-ti-1-"little"]|TI
        0000000001|MM|124|Levels|C0441889|["Levels"-ti-1-"levels"]|TI
        0000000001|MM|121|Exposure to|C0332157|["Exposure"-ti-1-"exposure"]|TI
        0000000001|MM|121|Injury due to exposure to external cause|C0274281|["Exposure, NOS"-ti-1-"exposure"]|TI
        0000000001|MM|121|Persons|C0027361|["People"-ti-1-"people"]|TI
        0000000001|MM|114|Old|C0580836|["Old"-ti-1-"older"]|TI
        0000000001|MM|114|Old episode|C0677546|["Old"-ti-1-"older"]|TI
        0000000001|MM|114|Known|C0205309|["Known"-ti-1-"known"]|TI
        <<<<< MMI
        """)
        mm_chunkmap=chunkmap_factory({'123.txt': [0, 1]})

        self.mo=MetamapOutput(mm_file,
                              [">>>>> MMI", "<<<<< MMI", "* error *"],
                              mm_chunkmap)
    def testMetamapBuilderEmptySet(self):
        my_builder=MetamapCooccurrenceGraphBuilder()
        graph=my_builder.create_graph([])
        self.assert_(type(graph) is Graph)
    def testMetamapBuilderBuildsGraphs(self):
        my_builder=MetamapCooccurrenceGraphBuilder()
        graphs=[my_builder.create_graph(x.lines) for x in self.mo]
        # There should be only one graph
        self.assertEqual(1, len(graphs))
        # It should have a boatload of relationships
        matrix=graphs[0].as_mapped_link_matrix()
        # There are 15 unique elements in the fake METAMAP file
        self.assertEqual(15, len(matrix))

if __name__ == '__main__':
    unittest.main()