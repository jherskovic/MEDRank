#!/usr/bin/env python
# encoding: utf-8
"""
infer_relation_direction.py

Uses MRREL to infer a relation's directionality, given two CUIs.

Created by Jorge Herskovic on 2008-06-24.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""
import os.path
import operator
import sys
from MEDRank.utility import cache
from MEDRank.utility.logger import logging, ULTRADEBUG
#from MEDRank.file.mrrel import (MRRELTable, MRRELLine)
_DEFAULT_FILE_NAME=os.path.join(cache.path(), 
                                   "direction_inference.p.bz2")


class RelationDirectionInferrer(dict):
    def build_from_mrrel_file_and_stype_table(self, mrrel_table,
                                              semantic_types):
        """Builds a relationship dictionary and stores a semantic type 
        table."""
        count=0
        self._stypes=semantic_types
        for l in mrrel_table:
            if l.original_direction:
                if l.cui1==l.cui2: # Relationships of a concept to itself are
                                   # not interesting to us.
                    continue
                # n^2 computation FTW!
                tuis1=semantic_types.get(l.cui1, [])
                tuis2=semantic_types.get(l.cui2, [])
                for t1 in tuis1:
                    for t2 in tuis2:
                        try:
                            self[(t1, t2)]+=1
                        except KeyError:
                            self[(t1, t2)]=1
                        try:
                            self[(t2, t1)]-=1
                        except KeyError:
                            self[(t2, t1)]=1
            count+=1
            if (count % 1000)==0: logging.debug("%d lines processed", count)
    def infer_relation_direction(self, cui1, cui2, threshold=0.3):
        """Returns 1 if the relation is cui1->cui2, -1 if it's cui2->cui1, 
        0 if it doesn't know.
        
        The reverse relationship cases are covered when building the
        dictionary.
        """
        tuis1=self._stypes.get(cui1, [])
        tuis2=self._stypes.get(cui2, [])
        values=[0] # Just to make sure there's something to return later
        for t1 in tuis1:
            for t2 in tuis2:
                values.append(self.get((t1, t2), 0))
        maxabs=float(reduce(operator.add, (abs(x) for x in values)))
        if maxabs==0:
            return 0
        result=reduce(operator.add, (x/maxabs for x in values))
        logging.log(ULTRADEBUG, "Decision for %s<-?->%s: %1.5f", cui1, cui2, result)
        if result>threshold:
            return 1
        if result<(-threshold):
            return -1
        return 0