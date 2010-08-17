#!/usr/bin/env python
# encoding: utf-8
"""
test_text.py

Created by Jorge Herskovic on 2008-05-29.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import unittest
from MEDRank.file.text import *

# pylint: disable-msg=C0103,C0111,R0904,W0612
class textTests(unittest.TestCase):
    def setUp(self):
        import StringIO
        testfile=StringIO.StringIO("""
        
        First line    
        # comment
        second line""")
        self.original_file=testfile
        self.my_file=Text(testfile)
    def testCount(self):
        """The iteration should return only two lines"""
        count=0
        for line in self.my_file:
            count+=1
        self.assertEqual(count, 2)
    def testContents(self):
        lines=[]
        for l in self.my_file:
            lines.append(l)
        self.assertEqual(lines, ['First line', 'second line'])
    def testGenerator(self):
        lines=[x for x in self.my_file]
        self.assertEqual(lines, ['First line', 'second line'])
    def testList(self):
        self.assertEqual(self.my_file.as_list(),
                        ['First line', 'second line'])
    def testDict(self):
        self.assertEqual(self.my_file.as_dict(),
                        {'First line': None, 'second line': None})
    def testDictWithValue(self):
        self.assertEqual(self.my_file.as_dict(0),
                        {'First line': 0, 'second line': 0})
    def testConsumption(self):
        self.assertEqual(self.my_file.as_dict(0),
                        {'First line': 0, 'second line': 0})
        # The file should be consumed at this point
        self.assertEqual(self.my_file.as_list(), [])
    def testRewinding(self):
        self.assertEqual(self.my_file.as_dict(0),
                        {'First line': 0, 'second line': 0})
        # The file should be consumed at this point
        self.assertEqual(self.my_file.as_list(), [])
        # Rewind, and we get our data back
        self.my_file.rewind()
        self.assertEqual(self.my_file.as_dict(0),
                        {'First line': 0, 'second line': 0})
    def test_file_property(self):
        self.assertEqual(self.my_file.original_file, self.original_file)
        
if __name__ == '__main__':
    unittest.main()