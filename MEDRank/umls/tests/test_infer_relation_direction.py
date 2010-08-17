#!/usr/bin/env python
# encoding: utf-8
"""
test_infer_relation_direction.py

Created by Jorge Herskovic on 2008-06-24.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import unittest
import sys
sys.path.append('../')
from infer_relation_direction import *
from MEDRank.file.mrrel import *
from StringIO import StringIO
class test_infer_relation_direction(unittest.TestCase):
    def setUp(self):
        self.fakefile=StringIO("""
C0000005|A7755565|SCUI|RB|C0036775|A0115649|SCUI||R31979041||MSH|MSH|||N||
C0000039|A0016511|AUI|SY|C0000039|A1317687|AUI|permuted_term_of|R28482429||MSH|MSH|||N||
C0000039|A0016514|AUI|SY|C0000039|A1317707|AUI|permuted_term_of|R28482431||MSH|MSH|||N||
C0000039|A0016515|AUI|AQ|C0001555|A3879702|AUI||R53088417||MSH|MSH|||N||
C0000039|A0016515|AUI|AQ|C0001688|A3879703|AUI||R53088418||MSH|MSH|||N||
C0000039|A0016515|AUI|AQ|C0002776|A3879704|AUI||R53088419||MSH|MSH|||N||
C0000039|A0016515|AUI|AQ|C0003139|A3879707|AUI||R53088421||MSH|MSH|||N||
C0000039|A0016515|AUI|AQ|C0005572|A3879708|AUI||R53088422||MSH|MSH|||N||
C0000039|A0016515|AUI|AQ|C0005768|A3879709|AUI||R53088423||MSH|MSH|||N||
C0000039|A0016515|AUI|AQ|C0007807|A3879711|AUI||R53088424||MSH|MSH|||N||
C0000039|A0016515|AUI|AQ|C0007987|A3879712|AUI||R53088425||MSH|MSH|||N||
C0000039|A0016515|AUI|AQ|C0008903|A3879715|AUI||R53088427||MSH|MSH|||N||
C0000039|A0016515|AUI|AQ|C0011933|A3879722|AUI||R53088430||MSH|MSH|||N||
C0000039|A0016515|AUI|AQ|C0013557|A3879726|AUI||R53088431||MSH|MSH|||N||
C0000039|A0016515|AUI|AQ|C0017399|A3879733|AUI||R53088432||MSH|MSH|||N||
C0000039|A0016515|AUI|AQ|C0019665|A3879735|AUI||R53088433||MSH|MSH|||N||
        """)
        self.mrrel_reader=MRRELTable(self.fakefile)
    def testBuildEmptyDictionary(self):
        inferrer=RelationDirectionInferrer()
        inferrer.build_from_mrrel_file(self.mrrel_reader)
        # There's a lot of repetition in the original file. In fact, there are
        # only four different relationships, and none of them are original.
        self.assertEqual(0, len(inferrer))
    def testBuildSuccessfully(self):
        inferrer=RelationDirectionInferrer()
        inferrer.build_from_mrrel_file(MRRELTable(StringIO(""" C0000005|A7755565|SCUI|RB|C0036775|A0115649|SCUI||R31979041||MSH|MSH||Y|N||
C0000039|A0016511|AUI|SY|C0000039|A1317687|AUI|permuted_term_of|R28482429||MSH|MSH||Y|N||
        """)))
        # There should be 2 relationships there - one line is from a concept
        # to itself
        self.assertEqual(2, len(inferrer))
        self.assertEqual(1, inferrer.infer_relation_direction('c0000005',
                                                              'c0036775'))
        self.assertEqual(-1, inferrer.infer_relation_direction('c0036775',
                                                               'c0000005'))
        self.assertEqual(0, inferrer.infer_relation_direction('c9999999',
                                                              'c0036775'))

if __name__ == '__main__':
    unittest.main()