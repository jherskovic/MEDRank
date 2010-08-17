#!/usr/bin/env python
# encoding: utf-8
"""
names_and_ids.py

Handles the Names-and-corresponding-IDs in the UMLS to MeSH mappings.

Created by Jorge Herskovic on 2008-05-12.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

class NamesAndIDs(dict):
    def __init__(self, names, ids):
        if len(names)!=len(ids):
            raise ValueError("The length of Names and Identifiers must be "
                             "identical. I received these names: %r and "
                             "these identifiers %r." % (names, ids))
        for n,i in zip(names, ids):
           self[i]=n
    def iter_descriptors(self):
        """Iterator that returns only the descriptors"""
        for k in self:
            if k[0].lower()=="d":
                yield k
        return
    def iter_qualifiers(self):
        """Iterator that returns only the qualifiers"""
        for k in self:
            if k[0].lower()=='q':
                yield k
        return
