#!/usr/bin/env python
# encoding: utf-8
"""
build_concept_data_file.py

Takes the mappings provided by Olivier Bodenreider and turns them into a proper
data format for the MEDRank application. Namely, a database indexed by concept
name on the disk.

The format of the input file should be the one provided by Olivier. Here's the
description from MEDRank v1:

Contains code to handle the NLM UMLS->MeSH mapping files that live at
mor.nlm.nih.gov

(Many thanks to Olivier Bodenreider <olivier@nlm.nih.gov> for pointing 
us to these and describing the format)
The format description is copied from his email to us. Fields are separated
by |
1) type of mapping
  m = mapped to MeSH
  u = no mapping found
2) CUI
3) preferred name of the concept
4) method used for mapping
  No MeSH term mapped to (when 1 = u)
  I = synonymy
  A = associated expression
  G/P = graph of the ancestors, seeded by parents
  G/C = graph of the ancestors, seeded by children
  G/S = graph of the ancestors, seeded by siblings
  O = otherwise related concepts
5) semi-colon delimited list of identifiers in MeSH
  Dxxxxxx = descriptors (main headings)
  Qxxxxxx = qualifiers (subheadings)
  Cxxxxxx = supplementary concepts
6) semi-colon delimited list of names in MeSH
  (same order as the UIs)

The first parameter should be the desired filename for the data store, the
second should be the file to process. The third should be the file containing
the MRSTY table from the UMLS, to add information on the semantic types.

Created by Jorge Herskovic on 2008-05-12.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import bz2
import sys
import re
from MEDRank.utility.logger import logging
from MEDRank.umls.concrete_concept import ConcreteConcept
from MEDRank.file.disk_backed_dict import StringDBDict
from MEDRank.file.mrsty import MRSTYTable
from MEDRank.umls.semantic_types import SemanticTypes
from MEDRank.file.text import Text

def replace_only_within_parenthesis(string, to_replace, replacement):
    open_paren_count=0
    output=[]
    for character in string:
        if character=='(':
            open_paren_count+=1
            continue
        if character==')':
            open_paren_count-=1
        if character==to_replace and open_paren_count>0:
            output.append(replacement)
        else:
            output.append(character)
    return ''.join(output)

def build_concept_dictionary(original_file, dictionary_to_fill={}, 
                             semantic_types={}):
    """Takes the original file from the UMLS and uses it to fill in the
    provided dictionary (in this particular implementation, it should be a
    StringDBDict). The only cleverness here is that the name splitter has
    problems sometimes because there are chemical names that contain ; but
    are not a split character.
    Fortunately the stray ; are always contained within parenthesis, so it's
    easy to handle them properly. The complete name may also appear among 
    the names strings, and it's reasonable to assume that it should be kept
    whole (especially if it contains a ; as some names do)"""
    count=0
    for line in original_file:
        linesplit=line.split('|')
        m,CUI,UMLS_name,mapping_method=linesplit[:4]
        CUI=CUI.lower()
        is_mapped=(m=='m')
        if is_mapped:
            # Some name sequences have ; characters between parentheses. We'll
            # replace them with an unlikely sequence for the split # and then 
            # replace them back.
            names=replace_only_within_parenthesis(linesplit[5], ';', 
                                                  '#@&SEMICOLON&@#')
            # Also replace the original UMLS name, if it's in there, with 
            # a special token
            # names.replace(UMLS_name, '#@&original UMLS name&@#')
            ids=linesplit[4].split(';')
            names=names.split(';', len(ids) -1)# Assume that we want, at most,
                                               # the same number of items as 
                                               # the IDs (we thus want one 
                                               # split less than the len of
                                               # the IDs)
            #names=[x.replace('#@&original UMLS name&@#', UMLS_name) 
            #       for x in names]
            names=[x.replace('#@&SEMICOLON&@#', ';') for x in names]
        else:
            names,ids=[],[]
        try:
            try:
                st=semantic_types[CUI]
            except KeyError:
                #print "No semantic types found for %s" % CUI
                st=set()
            dictionary_to_fill[CUI]=ConcreteConcept(UMLS_name,
                                                 mapping_method,
                                                 names, ids,
                                                 st )
        except:
            print "Error while processing:", line
            raise
        count+=1
        if count%10000==0:
            print "Already processed %d UMLS concepts." % count
            sys.stdout.flush()
    return dictionary_to_fill
    
def main():

    mrsty_file=sys.argv[3]
    original_filename=sys.argv[2]
    data_store_name=sys.argv[1]
    original_file=Text(bz2.BZ2File(original_filename, 'r'))
    print "Loading semantic types from %s" % mrsty_file
    stypes=SemanticTypes()
    stypes.build_from_mrsty_file(MRSTYTable(bz2.BZ2File(mrsty_file)))
    print "Semantic types loaded."
    print "Turning the data from %s into %s. Please wait." % (
            original_filename, data_store_name)
    data_store=StringDBDict(data_store_name, 
                            sync_every_transactions=0,
                            write_out_every_transactions=200000,
                            file_mode='c')
    data_store.sync_every=0
    build_concept_dictionary(original_file, data_store, stypes)
    data_store.sync_every=100
    print "Conversion done."

if __name__ == '__main__':
    main()

