#!/usr/bin/env python
# encoding: utf-8
"""
test_vocabulary_vector.py

Created by Jorge Herskovic on 2008-05-29.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import unittest
from MEDRank.evaluation.vocabulary_vector import *


# pylint: disable-msg=C0103,C0111,R0904        
class vocabulary_vectorTests(unittest.TestCase):
    def setUp(self):
        self.my_vector=VocabularyVector(5)
    def testLength(self):
        self.assertEquals(len(self.my_vector), 5)
    def testStore(self):
        self.my_vector[1]=1.5
        self.assertEquals(self.my_vector[1], 1.5)
        self.assertEquals(self.my_vector[0], 0.0)
        self.assertEquals(self.my_vector[2], 0.0)
        self.assertEquals(self.my_vector[3], 0.0)
        self.assertEquals(self.my_vector[4], 0.0)
    def testSizeLimits(self):
        self.assertRaises(AssertionError, self.my_vector.__getitem__, 7)
        self.assertRaises(AssertionError, self.my_vector.__getitem__, -7)
    def testNegativeIndexing(self):
        self.my_vector[-1]=7
        self.assertEquals(self.my_vector[4], 7)
        self.assertEquals(self.my_vector[-1], 7)
        self.assertEquals(self.my_vector[3], 0.0)
        self.assertEquals(self.my_vector[-3], 0.0)
    def testMultipleAssignment(self):
        self.my_vector[-2]=7
        self.my_vector[1]=-9
        self.assertEquals(self.my_vector[3], 7)
        self.assertEquals(self.my_vector[1], -9)
        self.assertEquals(self.my_vector[2], 0.0)
    def testNonZero(self):
        self.my_vector[1]=8
        self.assertEquals(self.my_vector.nonzero(), [1])
        self.my_vector[3]=0.0 # Should delete the element
        self.assertEquals(self.my_vector.nonzero(), [1])
    def testAsList(self):
        self.assertEquals(self.my_vector.as_list(), [0.0, 0.0, 0.0, 0.0, 0.0])
        self.my_vector[1]=7.5
        self.assertEquals(self.my_vector.as_list(), [0.0, 7.5, 0.0, 0.0, 0.0])
        self.my_vector[4]=9.0
        self.assertEquals(self.my_vector.as_list(), [0.0, 7.5, 0.0, 0.0, 9.0])
    def testVectorLength(self):
        self.assertEquals(self.my_vector.length(), 0.0)
        self.my_vector[0]=3.0
        self.my_vector[2]=4.0
        self.assertEquals(self.my_vector.length(), 5.0)
    def testAdditionChecksForCorrectSize(self):
        another_vector=VocabularyVector(4)
        self.assertRaises(AssertionError, self.my_vector.__add__, another_vector)
    def testAddition(self):
        another_vector=VocabularyVector(5)
        vector_sum=self.my_vector+another_vector
        self.assertEquals(vector_sum[0], 0.0)
        self.assertEquals(vector_sum[1], 0.0)
        self.assertEquals(vector_sum[2], 0.0)
        self.assertEquals(vector_sum[3], 0.0)
        self.assertEquals(vector_sum[4], 0.0)
        self.my_vector[1]=1.5
        vector_sum=self.my_vector+another_vector
        self.assertEquals(vector_sum[0], 0.0)
        self.assertEquals(vector_sum[1], 1.5)
        self.assertEquals(vector_sum[2], 0.0)
        self.assertEquals(vector_sum[3], 0.0)
        self.assertEquals(vector_sum[4], 0.0)
        another_vector[1]=1.0
        vector_sum=self.my_vector+another_vector
        self.assertEquals(vector_sum[0], 0.0)
        self.assertEquals(vector_sum[1], 2.5)
        self.assertEquals(vector_sum[2], 0.0)
        self.assertEquals(vector_sum[3], 0.0)
        self.assertEquals(vector_sum[4], 0.0)
        another_vector[4]=7.0
        vector_sum=self.my_vector+another_vector
        self.assertEquals(vector_sum[0], 0.0)
        self.assertEquals(vector_sum[1], 2.5)
        self.assertEquals(vector_sum[2], 0.0)
        self.assertEquals(vector_sum[3], 0.0)
        self.assertEquals(vector_sum[4], 7.0)
        self.my_vector[3]=3.0
        vector_sum=self.my_vector+another_vector
        self.assertEquals(vector_sum[0], 0.0)
        self.assertEquals(vector_sum[1], 2.5)
        self.assertEquals(vector_sum[2], 0.0)
        self.assertEquals(vector_sum[3], 3.0)
        self.assertEquals(vector_sum[4], 7.0)
    def testDotChecksForCorrectSize(self):
        another_vector=VocabularyVector(4)
        self.assertRaises(AssertionError, self.my_vector.dot, another_vector)
    def testDotProduct(self):
        another_vector=VocabularyVector(5)
        dot=self.my_vector.dot(another_vector)
        self.assertEquals(dot, 0.0)
        self.my_vector[2]=2.0
        another_vector[2]=1.0
        dot=self.my_vector.dot(another_vector)
        self.assertEquals(dot, 2.0)
        another_vector[4]=8.0
        dot=self.my_vector.dot(another_vector)
        self.assertEquals(dot, 2.0)
    def testScale(self):
        scaled=self.my_vector.scale(0)
        self.assertEquals(scaled[0], 0.0)
        self.assertEquals(scaled[1], 0.0)
        self.assertEquals(scaled[2], 0.0)
        self.assertEquals(scaled[3], 0.0)
        self.assertEquals(scaled[4], 0.0)
        self.my_vector[1]=1.5
        self.my_vector[3]=3.0
        scaled=self.my_vector.scale(0)
        self.assertEquals(scaled[0], 0.0)
        self.assertEquals(scaled[1], 0.0)
        self.assertEquals(scaled[2], 0.0)
        self.assertEquals(scaled[3], 0.0)
        self.assertEquals(scaled[4], 0.0)
        scaled=self.my_vector.scale(1.0)
        self.assertEquals(scaled[0], 0.0)
        self.assertEquals(scaled[1], 1.5)
        self.assertEquals(scaled[2], 0.0)
        self.assertEquals(scaled[3], 3.0)
        self.assertEquals(scaled[4], 0.0)
        scaled=self.my_vector.scale(-1.0)
        self.assertEquals(scaled[0], 0.0)
        self.assertEquals(scaled[1], -1.5)
        self.assertEquals(scaled[2], 0.0)
        self.assertEquals(scaled[3], -3.0)
        self.assertEquals(scaled[4], 0.0)
        
if __name__ == '__main__':
    unittest.main()