#!/usr/bin/env python
# encoding: utf-8
"""
semantic_types.py

Stores the semantic types of all CUIs for easy retrieval.

Created by Jorge Herskovic on 2008-06-25.
Copyright (c) 2008 University of Texas - Houston. All rights reserved.
"""

class SemanticTypes(dict):
    def build_from_mrsty_file(self, file_ojbect):
        """Reads an MRSTY file and fills in the dictionary from it."""
        for line in file_ojbect:
            if line.cui in self:
                self[line.cui].add(line.tui)
            else:
                self[line.cui]=set([line.tui])
        return
    
