#!/usr/bin/env python
# encoding: utf-8
"""
test_link.py

Created by Jorge Herskovic on 2008-05-29.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import unittest
from MEDRank.computation.link import *
from MEDRank.computation.node import Node
import random

# pylint: disable-msg=C0103,C0111
class linkTests(unittest.TestCase):
    def setUp(self):
        self.normalLink=Link('a', 'b', 1.0)
        self.nullLink=Link('a', 'b', 0.0)
        self.reverseLink=Link('a', 'b', -1.0)
    def testRepresentations(self):
        self.assertEqual(repr(self.normalLink), 
                         "<Link: 'a'--1.0000000-->'b'>")
        self.assertEqual(repr(self.nullLink), "<Link: 'a' -0- 'b'>")
        self.assertEqual(repr(self.reverseLink), 
                         "<Link: 'b'--1.0000000-->'a'>")
    def testADirectedLink(self):
        self.adirected=AdirectionalLink('a', 'b', 1.0)
        self.assertEqual(self.adirected.weight, 1.0)
    def testAdirectedNegativeLink(self):
        self.adirected=AdirectionalLink('a', 'b', -1.0)
        self.assertEqual(self.adirected.weight, 1.0)
    def testAdirectedNegativeLinkSetter(self):
        self.adirected=AdirectionalLink('a', 'b', 0.0)
        self.assertEqual(self.adirected.weight, 0.0)
        self.adirected.weight=-1.0
        self.assertEqual(self.adirected.weight, 1.0)
    def testEquivalence(self):
        self.assertNotEqual(self.normalLink, self.reverseLink)
        self.assertEqual(self.normalLink, self.nullLink)
    def testNames(self):
        self.normalLink.name="interesting_link"
        self.assertEqual(self.normalLink.name, "interesting_link")
        self.assertEqual("<Link interesting_link: 'a'--1.0000000-->'b'>",
                         repr(self.normalLink))
    def testADirLinkRepresentation(self):
        self.adirected=AdirectionalLink('a', 'b', -1.0)
        self.assertEqual(repr(self.adirected), 
                         "<Link: 'a'==1.0000000=='b'>")
    def testADirEquivalence(self):
        self.adirected=AdirectionalLink('a', 'b', -1.0)
        self.adirected2=AdirectionalLink('a', 'b', 1.0)
        self.assertEqual(self.adirected, self.adirected2)
        self.adirected3=AdirectionalLink('b', 'a', 1.0)
        self.assertEqual(self.adirected, self.adirected3)
    def testHashing(self):
        self.assertEqual(hash(self.normalLink), hash(self.nullLink))
        self.assertNotEqual(hash(self.normalLink), hash(self.reverseLink))
        self.adirected=AdirectionalLink('a', 'b', -1.0)
        self.adirected2=AdirectionalLink('a', 'b', 1.0)
        self.assertEqual(hash(self.adirected), hash(self.adirected2))
        self.adirected3=AdirectionalLink('b', 'a', 1.0)
        self.assertEqual(hash(self.adirected), hash(self.adirected3))
    def testNodeLinks(self):
        n=Node("c1234", "Fake node", 0.987)
        n2=Node("c45678", "Another fake node", 0.123)
        linky=Link(n, n2, 1)
        linky2=Link(n, n2, -1)
        linky3=Link(n2, n, 1)
        self.assertNotEqual(linky, linky2) # The direction is the opposite
        self.assertEqual(linky2, linky3)
        self.assertNotEqual(linky, linky3)
        # The hashes must match too
        self.assertNotEqual(hash(linky), hash(linky2)) # The direction is the opposite
        self.assertEqual(hash(linky2), hash(linky3))
        self.assertNotEqual(hash(linky), hash(linky3))
    def testForHashClashesNumberOfRandomNodes(self):
        for x in xrange(1000000):
            nid1="C%07d" % random.randint(0, 9999999)
            nid2="C%07d" % random.randint(0, 9999999)
            nid3="C%07d" % random.randint(0, 9999999)
            n1=Node(nid1, "Fake node", 1)
            n2=Node(nid2, "Fake node 2", 1)
            n3=Node(nid3, "Yet Another Fake Node", 1)
            linky=Link(n1, n2, 1)
            linky2=Link(n1, n3, 1)
            if nid2==nid3:
                # Very infrequent!
                self.assertEqual(hash(linky), hash(linky2))
            else:
                self.assertNotEqual(hash(linky), hash(linky2))
                
if __name__ == '__main__':
    unittest.main()