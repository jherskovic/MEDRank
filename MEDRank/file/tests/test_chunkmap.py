#!/usr/bin/env python
# encoding: utf-8
"""
test_chunkmap.py

Created by Jorge Herskovic on 2008-05-29.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import unittest
from MEDRank.file.chunkmap import *

# pylint: disable-msg=C0103,C0111
class chunkmapTests(unittest.TestCase):
    def setUp(self):
        self.original_dict={'12345.txt': [1,2,3], '6789.txt': [4,5,6]}
        self.useless_dict={12345:12345, 6789:6789}
    def test_original(self):
        oc=OriginalChunkmap(self.original_dict)
        self.assertEquals(oc['12345.txt'], [1, 2, 3])
        self.assertEquals(oc.pmid_from_block(2), Pmid(12345))
        self.assertEquals(oc.pmid_from_block(6), Pmid(6789))
        self.assertRaises(KeyError, oc.pmid_from_block, 999)
    def test_useless(self):
        uc=UselessChunkmap(self.useless_dict)
        self.assertEquals(Pmid(6789), uc.pmid_from_block(6789))
    def test_guess_useless(self):
        somechunkmap=chunkmap_factory(self.useless_dict)
        self.assert_(isinstance(somechunkmap, UselessChunkmap))
    def test_guess_original(self):
        somechunkmap=chunkmap_factory(self.original_dict)
        self.assert_(isinstance(somechunkmap, OriginalChunkmap))

if __name__ == '__main__':
    unittest.main()