#!/usr/bin/env python
# encoding: utf-8
"""
test_metamap_machine_output.py

Created by Jorge Herskovic on 2008-06-07.
Copyright (c) 2008 University of Texas - Houston. All rights reserved.
"""

import unittest
from MEDRank.file.metamap_machine_output import *


class test_metamap_machine_output(unittest.TestCase):
    def setUp(self):
        self.uttext="""utterance('98157484.ab.1',"OBJECTIVE: """\
                    """To define the total allowable variability that is"""\
                    """ clinically tolerated for certain drug assays """\
                    """performed by the therapeutic drug monitoring (TDM)"""\
                    """ laboratory at our institution.")."""
        self.mapline="mappings([map(-901,[ev(-660,'C0038317',steroid,"\
            "'Steroids',[steroid],[strd],[[[1,1],[1,1],0]],no,no)"\
            ",ev(-901,'C0312426','Hormone production','Hormone production'"\
            ",[hormone,production],[ortf],[[[2,2],[1,1],0],"\
            "[[3,3],[2,2],0]],yes,no)]),map(-901,[ev(-734,"\
            "'C0301818','Steroid hormone','Steroid hormone',"\
            "[steroid,hormone],"\
            "[horm,strd],[[[1,2],[1,2],0]],no,no),ev(-827,'C1548180'"\
            ",'Production','Production Processing ID',[production],"\
            "[fndg],[[[3,3],[1,1],0]],yes,no)]),map(-901,[ev(-734,"\
            "'C0301818',"\
            "'Steroid hormone','Steroid hormone',[steroid,hormone],"\
            "[horm,strd],"\
            "[[[1,2],[1,2],0]],no,no),ev(-827,'C0033268',"\
            "production,production,[production],[ocac],"\
            "[[[3,3],[1,1],0]],yes,no)])])."""
    def testUtteranceIdentifiesLineID(self):
        utline=UtteranceLine(self.uttext)
        self.assertEqual(98157484, utline.line_id)
    def testConceptExtraction(self):
        ml=MappingLine(self.mapline)
        c=[x for x in ml.iter_concepts()]
        self.assertEqual('c0038317', c[0].CUI)
        self.assertEqual('c0312426', c[1].CUI)
    def testLineFactory(self):
        self.assert_(type(line_factory(self.uttext)) is UtteranceLine)
        self.assert_(type(line_factory(self.mapline)) is MappingLine)
    def testLineFactoryFailsOnGibberish(self):
        self.assertRaises(WrongTypeOfLineError, line_factory, "ooga booga")
        
if __name__ == '__main__':
    unittest.main()