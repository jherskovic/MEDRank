#!/usr/bin/env python
# encoding: utf-8
"""
test_semrep.py

Created by Jorge Herskovic on 2008-05-29.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import unittest
from MEDRank.file.semrep import *

# pylint: disable-msg=C0103,C0111,R0904        
class semrepTests(unittest.TestCase):
    def setUp(self):
        import StringIO
        from MEDRank.file.chunkmap import chunkmap_factory
        # Fake file taken from actual SEMREP output.
        # No animals were harmed in the making of this test.
        # The output doesn't really make total sense, but to keep the volume
        # of data at a reasonable level we'll use a small, senseless file.
        self.fakefile=\
                 StringIO.StringIO("SE|0000000000||ti|2|entity|Affecting|"
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
                                   "USELESS LINE!\n"
                                   "SE|0000000000||ti|3|text|Coactivator and"
                                   " corepressor proteins have recently been"
                                   " identified that interact with steroid"
                                   " hormone receptors and modulate"
                                   " transcriptional activation\n")
        self.fake_chunkmap=chunkmap_factory({'123.txt': [0]})
    def testCreateSRFile(self):
        sro=SemrepOutput(self.fakefile, [], self.fake_chunkmap)
        self.assert_(sro is not None)
    def getArticles(self):
        sro=SemrepOutput(self.fakefile, ["USELESS LINE!"],
                         self.fake_chunkmap)
        self.articles=[x for x in sro]
    def testIteration(self):
        self.getArticles()
        self.assertEquals(len(self.articles), 1)
    def testExtractionLength(self):
        self.getArticles()
        self.assertEquals(len(self.articles[0].lines), 4)
    def testEntities(self):
        self.getArticles()
        article=self.articles[0]
        self.assert_(isinstance(article.lines[0], EntityLine))
        self.assert_(isinstance(article.lines[1], EntityLine))
        self.assertEquals(article.lines[0].CUI, 'c0392760')
        self.assertEquals(article.lines[1].CUI, 'c1314939')
    def testRelations(self):
        self.getArticles()
        article=self.articles[0]
        self.assert_(isinstance(article.lines[2], RelationLine))
        self.assertEquals(article.lines[2].CUI1, 'c0301818')
        self.assertEquals(article.lines[2].CUI2, 'c0597519')
        self.assertEquals(article.lines[2].relation_type, 'interacts_with')
    def testTextLinePresent(self):
        self.getArticles()
        the_line=[x for x in self.articles[0].lines if type(x) is TextLine]
        self.assertEquals(len(the_line), 1)
    # The exceptions are raised in a specific order according to the parsing
    # order. The test suite takes this into account.
    def testBadEntityLineRaisesCUIError(self):
        bad_line="SE|0000000000||ti|2|entity|Affecting|" \
                 "ftcn||involved||||1000|319|326\n"
        raised=False
        try:
            EntityLine(bad_line)
        except CUINotFoundError:
            raised=True
        self.assert_(raised)
    def testNoEntityLineRaisesLineIDError(self):
        raised=False
        try:
            EntityLine('SE|')
        except NoLineIDError:
            raised=True
        self.assert_(raised)
    def testPartialEntityLineRaisesCUIError(self):
        raised=False
        try:
            EntityLine('SE|0000000000||ti|2|entity|Affecting')
        except CUINotFoundError:
            raised=True
        self.assert_(raised)
    def testEntityNoConfidenceError(self):
        raised=False
        try:
            EntityLine("SE|0000000000||ti|2|entity|Affecting|"
                       "ftcn|C0392760|involved|||||319|326\n")
        except NoConfidenceError:
            raised=True
        self.assert_(raised)
    def testUnknownLineTypeError(self):
        raised=False
        try:
            SemrepOutput.line_factory(
                "SE|0000000000||ti|2|BAD_TYPE|Affecting|"
                "ftcn|C0392760|involved|||||319|326\n")
        except UnknownLineTypeError:
            raised=True
        self.assert_(raised)
    def testNoLineTypeError(self):
        raised=False
        try:
            SemrepOutput.line_factory("This line has no divisors, and thus no type")
        except NoLineTypeError:
            raised=True
        self.assert_(raised)
    
if __name__ == '__main__':
    unittest.main()