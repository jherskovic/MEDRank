#!/usr/bin/env python
# encoding: utf-8
"""
test_nlm_output.py

Created by Jorge Herskovic on 2008-05-29.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import unittest
import sys
sys.path.append('../')
from MEDRank.file.nlm_output import *

# pylint: disable-msg=C0103,C0111,R0904        
class nlm_outputTests(unittest.TestCase):
    def setUp(self):
        import StringIO
        self.fakefile=StringIO.StringIO("""
        12345|Boo|Hiss
        
        56789|Woo|Hoo
        * ERROR *
        56790|Woo|Boo""")
        self.lines_to_skip=['* ERROR *']
    def testLine(self):
        l=Line('1234|XYZ|ABC')
        self.assertEquals(l.line_id, 1234)
    def testLineFailsIfNothingToSplit(self):
        raised=False
        try:
            Line('')
        except NoLineIDError:
            raised=True
        self.assert_(raised)
    def testBuildingLineList(self):
        l1=Line('1234|XYZ|ABC')
        l2=Line('5678|DEF|QAZ')
        ll=LineList(1, [l1, l2])
        self.assertEquals(ll.set_id, 1)
        self.assertEquals(ll.lines, [l1, l2])
    def testNLMOutputIterator(self):
        no=NLMOutput(self.fakefile, Line, self.lines_to_skip)
        processed_lines=[x for x in no]
        self.assertEquals(processed_lines[0].line_id, 12345)
        self.assertEquals(processed_lines[1].line_id, 56789)
        self.assertEquals(processed_lines[2].line_id, 56790)
        self.assertEquals(3, len(processed_lines))
    def testChunkedOutput(self):
        from MEDRank.file.chunkmap import chunkmap_factory
        from MEDRank.pubmed.pmid import Pmid
        _cm={'1.txt': [12345], '2.txt': [56789, 56790]}
        cm=chunkmap_factory(_cm)
        cno=ChunkedNLMOutput(self.fakefile, Line, self.lines_to_skip, cm)
        processed_sets=[x for x in cno]
        self.assertEquals(len(processed_sets), 2)
        self.assertEquals(len(processed_sets[0].lines), 1)
        self.assertEquals(len(processed_sets[1].lines), 2)
        self.assertEquals(processed_sets[0].set_id, Pmid(1))
        self.assertEquals(processed_sets[1].set_id, Pmid(2))
        self.assertEquals(processed_sets[1].lines[1].line_id, 56790)
    def testExceptionIgnoring(self):
        class MyBadParser(NLMOutput):
            """This test class ignores NoLineID exceptions to parse the file,
            instead of specifying an Ignore line."""
            def ignore_exception(self, which_exception, on_which_line):
                return isinstance(which_exception, NoLineIDError)
        no=MyBadParser(self.fakefile, Line, [])
        # It should have the same output as testNLMOutputIterator
        processed_lines=[x for x in no]
        self.assertEquals(processed_lines[0].line_id, 12345)
        self.assertEquals(processed_lines[1].line_id, 56789)
        self.assertEquals(processed_lines[2].line_id, 56790)
        self.assertEquals(3, len(processed_lines))
    def testDecoratedLineExtractionWorks(self):
        l=Line('12345.decorated.badly|xyz|abc')
        self.assertEquals(l.line_id, 12345)
    def testOtherSeparationCharactersWork(self):
        l=Line('12345\tXYZ\tABC', split_char='\t')
        self.assertEquals(l.line_id, 12345)
        
        
if __name__ == '__main__':
    unittest.main()