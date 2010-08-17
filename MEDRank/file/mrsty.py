#!/usr/bin/env python
# encoding: utf-8
"""
mrsty.py

Read support for UMLS MRSTY files (semantic type descriptions)

Created by Jorge Herskovic on 2008-06-25.
Copyright (c) 2008 University of Texas - Houston. All rights reserved.
"""

from MEDRank.file.nlm_output import NLMOutput

class MRSTYLine(object):
    """The line format (copied from the UMLS site):
    There is exactly one row in this file for each Semantic Type assigned to each concept. All Metathesaurus concepts have at least one entry in this file. Many have more than one entry. The TUI, STN, and STY are all direct links to the UMLS Semantic Network (Section 3).

Idx    Col.    Description
0      CUI     Unique identifier of concept
1      TUI     Unique identifier of Semantic Type
2      STN     Semantic Type tree number
3      STY     Semantic Type. The valid values are defined in the Semantic
               Network.
4      ATUI    Unique identifier for attribute
5      CVF     Content View Flag. Bit field used to flag rows included in
               Content View. This field is a varchar field to maximize the
               number of bits available for use.
               
"""
    __slots__=['_cui', '_tui', '_type_name']
    def __init__(self, original_line):
        processed_line=original_line.split('|')
        self._cui=processed_line[0]
        self._tui=processed_line[1]
        self._type_name=processed_line[3]
    def cui_fget(self):
        "Getter for the cui property"
        return self._cui
    cui=property(cui_fget)
    def tui_fget(self):
        "Getter for the cui property"
        return self._tui
    tui=property(tui_fget)
    def type_name_fget(self):
        "Getter for the cui property"
        return self._type_name
    type_name=property(type_name_fget)
    def __repr__(self):
        return "<MRSTY line @%#x representing type %s for cui %s>" % (   
                id(self), self.type_name, self.cui)

class MRSTYTable(NLMOutput):
    """Although not strictly an NLMOutput file, for all practical purposes it
    has the same structure, so we use the same infrastructure to process it.
    """
    def __init__(self, fileobject):
        NLMOutput.__init__(self, fileobject, type_of_lines=MRSTYLine,
                           lines_to_ignore=[])


if __name__ == '__main__':
    unittest.main()