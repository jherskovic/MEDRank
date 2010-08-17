#!/usr/bin/env python
# encoding: utf-8
"""
test_SingletonStrings.py

Created by Jorge Herskovic on 2008-05-29.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import unittest
# Not an official part of MEDRank yet, so...
import sys; sys.path.append('../')
from singleton_strings import *

class SingletonStringsTests(unittest.TestCase):
    def setUp(self):
        self.string1=SingletonString("Mi mama me mima")
        self.string2=SingletonString("Mi mama me ama")
        self.string3=SingletonString("Amo a mi mama")
        self.string4=SingletonString("Mi mama me ama")
        self.string5=SingletonString("Short")
    def testRepeatedStorage(self):
        self.assertEqual(len(SingletonString.string_store), 3)
        self.assertEqual(len(SingletonString.reverse_mapping), 3)
    def testRetrieval(self):
        retrieved=str(self.string3)
        self.assertEqual(retrieved, "Amo a mi mama")
        self.assertNotEqual(retrieved, "Mi mama me ama")
    def testComparisonBetweenSingletons(self):
        self.assertEqual(self.string2, self.string4)
    def testDifferenceBetweenSingletons(self):
        self.assertNotEqual(self.string1, self.string4)
    def testComparisonToRegularString(self):
        self.assertEqual(self.string1, "Mi mama me mima")
        self.assertNotEqual(self.string2, "Mi mama me mima")
    def testInequalityComparisons(self):
        true_comparison=self.string3<self.string2
        false_comparison=self.string2>self.string1
        self.assertEqual(true_comparison, True)
        self.assertEqual(false_comparison, False)
        true_comparison=self.string3<=self.string2
        false_comparison=self.string2>=self.string1
        self.assertEqual(true_comparison, True)
        self.assertEqual(false_comparison, False)
    def testConcat(self):
        self.assertEqual(self.string1+self.string2, 'Mi mama me mima'
                                                    'Mi mama me ama')
        self.assertEqual(self.string1+' ', 'Mi mama me mima ')
    def testMult(self):
        self.assertEqual(self.string3*2, 'Amo a mi mamaAmo a mi mama')
    def testSecretIdentities(self):
        """The strings should have been added in the order in which they were
        created."""
        self.assertEqual(self.string1.secret_identity(), 0)
        self.assertEqual(self.string2.secret_identity(), 1)
        self.assertEqual(self.string3.secret_identity(), 2)
        self.assertEqual(self.string4.secret_identity(), 1)
        self.assertEqual(self.string5.secret_identity(), 'Short')
        
if __name__ == '__main__':
    unittest.main()