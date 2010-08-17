#!/usr/bin/env python
# encoding: utf-8
"""
test_metamap.py

Created by Jorge Herskovic on 2008-05-29.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import unittest
from MEDRank.file.metamap import *
from MEDRank.file.nlm_output import NoLineIDError

# pylint: disable-msg=C0103,C0111,R0904        
class metamapTests(unittest.TestCase):
    def setUp(self):
        import StringIO
        from MEDRank.file.chunkmap import chunkmap_factory
        # Data from an actual file, with a few additions
        self.fakefile=StringIO.StringIO("""
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
        self.lines_to_ignore=[">>>>> MMI", "<<<<< MMI", "* error *"]
        self.fake_chunkmap=chunkmap_factory({'123.txt': [0],
                                             '345.txt': [1]})
        self.mo=MetamapOutput(self.fakefile, self.lines_to_ignore,
                              self.fake_chunkmap)
    def testBuildReader(self):
        self.assert_(self.mo is not None)
    def testIterationLength(self):
        output=[x for x in self.mo]
        self.assertEquals(2, len(output))
    def testSomeCUIsAreReadCorrectly(self):
        output=[x for x in self.mo]
        self.assertEquals(output[1].lines[1].confidence, 0.424)
        self.assertEquals(output[1].lines[2].CUI, 'c1706907')
    def testAllLinesAreMetamapLines(self):
        for article in self.mo:
            for each_line in article.lines:
                self.assert_(type(each_line) is MetamapLine)
    def testLineWithNoIDRaisesError(self):
        raised=False
        try:
            MetamapLine('quack')
        except NoLineIDError:
            raised=True
        self.assert_(raised)
    def testLineWithNoCUIRaisesError(self):
        raised=False
        try:
            MetamapLine('1234|MM|121|Injury||[blah]|TI')
        except CUINotFoundError:
            raised=True
        self.assert_(raised)
    def testOtherParsingErrors(self):
        raised=False
        try:
            # No source
            MetamapLine('1234|MM|121|Injury|c1234|[blah]')
        except ParsingError:
            raised=True
        self.assert_(raised)
    def testNoConfidenceError(self):
        raised=False
        try:
            MetamapLine('1234|MM||Injury|c1234|[blah]|TI')
        except NoConfidenceError:
            raised=True
        self.assert_(raised)
        
if __name__ == '__main__':
    unittest.main()