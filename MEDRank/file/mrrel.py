#!/usr/bin/env python
# encoding: utf-8
"""
mrrel.py

Reads an MRREL file from the UMLS distribution.

Created by Jorge Herskovic on 2008-06-23.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

from MEDRank.file.text import Text
from MEDRank.file.nlm_output import NLMOutput

class MRRELLine(object):
    """Represents a single line of an MRREL file. We only get the items that
    are of interest to MEDRank at the moment. The format of an MRREL line is:
    (taken from http://www.nlm.nih.gov/research/umls/meta2.html)
    
    There is one row in this table for each relationship between concepts or atoms known to the Metathesaurus, with the following exceptions found in other files: co-occurrences found in MRCOC.RRF, and pair-wise mapping relationships between two source vocabularies found in MRMAP.RRF and MRSMAP.RRF.

    Note that for asymmetrical relationships there is one row for each direction of the relationship. Note also the direction of REL - the relationship which the SECOND concept or atom (with Concept Unique Identifier CUI2 and Atom Unique Identifier AUI2) HAS TO the FIRST concept or atom (with Concept Unique Identifier CUI1 and Atom Unique Identifier AUI1).

Idx Col.     Description
  0 CUI1     Unique identifier of first concept
  1 AUI1     Unique identifier of first atom
  2 STYPE1   The name of the column in MRCONSO.RRF that contains the
             identifier used for the first concept or first atom in source of
             the relationship.
  3 REL      Relationship of second concept or atom to first concept or atom
  4 CUI2     Unique identifier of second concept
  5 AUI2     Unique identifier of second atom
  6 STYPE2   The name of the column in MRCONSO.RRF that contains the
             identifier used for the second concept or second atom in the
             source of the relationship.
  7 RELA     Additional (more specific) relationship label (optional)
  8 RUI      Unique identifier of relationship
  9 SRUI     Source asserted relationship identifier, if present
 10 SAB      Abbreviated source name of the source of relationship. Maximum
             field length is 20 alphanumeric characters.  Two source
             abbreviations are assigned: 
                 * Root Source Abbreviation (RSAB) — short form, no version
                   information, for example, AI/RHEUM, 1993, has an RSAB of
                   "AIR"
                 * Versioned Source Abbreviation (VSAB) — includes version
                   information, for example, AI/RHEUM, 1993, has an VSAB of
                   "AIR93"
             Official source names, RSABs, and VSABs are included in Appendix
             B.4.
 11 SL       Source of relationship labels
 12 RG       Relationship group. Used to indicate that a set of relationships
             should be looked at in conjunction.
 13 DIR      Source asserted directionality flag. Y indicates that this is the
             direction of the relationship in its source; N indicates that it
             is not; a blank indicates that it is not important or has not yet
             been determined.
 14 SUPPRESS Suppressible flag. Values = O, Y, E, or N. Reflects the
             suppressible status of the relationship; not yet in use. See also
             SUPPRESS in MRCONSO.RRF and MRDEF.RRF and MRREL.RRF.
 15 CVF      Content View Flag. Bit field used to flag rows included in
             Content View. This field is a varchar field to maximize the
             number of bits available for use.
    
    According to this description, we want the third, seventh, and fourth
    fields (2, 6, and 3 in indexing terms.)
    
    This class describes FROM-->REL-->TO relationships, which is the opposite 
    of the descriptions in the actual files (which are rel1<-rel<-rel2) 
    
    """
    __slots__=['_cui1', '_stype1', '_cui2', '_stype2', '_reltype', '_dir',
               '_original_direction']
    def __init__(self, original_line):
        processed_line=original_line.split('|')
        # Yes, the swap below is intentional. The UMLS describes relationships
        # in a to, rel, from format I dislike.
        # The directional flag also has a different meaning - I use it as 
        # "specified in the source or not"
        self._cui1=processed_line[0]
        self._cui2=processed_line[4]
        self._stype2=processed_line[2]
        self._stype1=processed_line[6]
        self._reltype=processed_line[3]
        self._dir=processed_line[13]!=''
        self._original_direction=processed_line[13]=='y'
    # The stype1 property.
    def stype1_fget(self):
        "Getter for the stype1 property"
        return self._stype1
    stype1=property(stype1_fget)
    # The stype2 property.
    def stype2_fget(self):
        "Getter for the stype2 property"
        return self._stype2
    stype2=property(stype2_fget)
    # The reltype property.
    def reltype_fget(self):
        "Getter for the reltype property"
        return self._reltype
    reltype=property(reltype_fget)
    def cui1_fget(self):
        "Getter for the cui1 property"
        return self._cui1
    cui1=property(cui1_fget)
    def cui2_fget(self):
        "Getter for the cui2 property"
        return self._cui2
    cui2=property(cui2_fget)
    def dir_fget(self):
        "Getter for the directional property"
        return self._dir
    directional=property(dir_fget)
    # The original_direction property.
    def original_direction_fget(self):
        "Getter for the original_direction property"
        return self._original_direction
    original_direction=property(original_direction_fget)
    def __repr__(self):
        return "<MRREL line @ %#x representing %s-(%s)->%s" % (id(self),
                                                               self.cui1,
                                                               self.reltype,
                                                               self.cui2)

class MRRELTable(NLMOutput):
    """Although not strictly an NLMOutput file, for all practical purposes it
    has the same structure, so we use the same infrastructure to process it.
    """
    def __init__(self, fileobject):
        NLMOutput.__init__(self, fileobject, type_of_lines=MRRELLine,
                           lines_to_ignore=[])
