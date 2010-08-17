#!/usr/bin/env python
# encoding: utf-8
"""
test_mti.py

Created by Jorge Herskovic on 2008-05-29.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import unittest
from MEDRank.file.mti import *

class mtiTests(unittest.TestCase):
    def setUp(self):
        import StringIO
        from MEDRank.file.chunkmap import chunkmap_factory
        #logging.basicConfig(level=logging.INFO,
        #                  format='%(asctime)s %(levelname)s %(message)s')
        
        # Data from an actual file, with a few additions
        self.fakefile=StringIO.StringIO("""
        16606471|*Pancreatitis, Acute Necrotizing|C0267941|46152|MH|RtM via: Pancreatitis, Acute Necrotizing|TI;AB|MM;RC
        16606471|*Randomized Controlled Trials as Topic|C0282440|19056|MH|RtM via: Randomized Controlled Trials as Topic|TI;AB|MM;RC
        16606471|Pancreatitis|C0030305|6224|MH|RtM via: Pancreatitis|AB|MM;RC
        16606471|Multicenter Studies as Topic|C0282439|4703|MH|||RC
        16606471|Sample Size|C0242618|3713|MH|RtM via: Sample Size|AB|MM;RC
        16606471|Double-Blind Method|C0013072|3524|MH|||RC
        16606471|*Clinical Trials as Topic|C0008976|2835|MH|RtM via: Clinical Trials|TI|MM
        16606471|Debridement|C0011079|1457|MH|RtM via: Debridement|AB|MM;RC
        16606471|Pancreas|C0030274|1387|MH|||RC
        16606471|Drainage|C0013103|1228|MH|RtM via: Drainage procedure|AB|MM;RC
        ------
        16606471|Patient Selection|C0242802|918|MH|||RC
        16606471|Laparotomy|C0023038|867|MH|RtM via: Laparotomy|AB|MM;RC
        """)
        self.fake_chunkmap=chunkmap_factory({16606471: 16606471})
    def testBuildsCorrectly(self):
        raised=False
        try:
            self.parser=MtiOutput(self.fakefile, DEFAULT_LINES_TO_IGNORE, 
                                  self.fake_chunkmap)
        except:
            raised=True
        self.assertFalse(raised)
    def testIterationLength(self):
        self.testBuildsCorrectly()
        output=[x for x in self.parser]
        self.assertEquals(1, len(output))

if __name__ == '__main__':
    unittest.main()