#!/usr/bin/env python
# encoding: utf-8
"""
restrict_to_mesh_converter.py

Filtering rules mimic MTI's rules - they were kindly provided by Jim Mork @ NLM.
Rules in English available as comments in the module itself.

Created by Jorge Herskovic on 2010-01-20.
Copyright (c) 2010 UTHSC School of Health Information Sciences. All rights reserved.
"""

#Please keep in mind that
#these are removals based on our specific use in the Medical
#Text Indexer (MTI) application and might be reasonable for
#other applications.  Also, please note this is based on the
#UMLS 2009AB and doesn't reflect 2010AA yet.
#
# /*  Remove full lines for extraneous -
#      "roman numeral" and roman numerals entries,
#       list of bad number entries,
#       only numbers and only numbers and symbols entries,
#       anything assigned Demography without a Demography
#       term, print entry term, or entry term is removed.
#  */
#
#Removing Roman Numeral: C0439067|Roman numeral|
#Removing Roman Numeral: C0439068|roman numeral upper case eye|
#Removing Roman Numeral: C0439069|Roman numeral II|
#Removing Roman Numeral: C0439070|Roman Numeral III|
#Removing Roman Numeral #: C0445385|VII|
#Removing Number: C0450340|1:1.5|
#Removing Number Lookup: C0450349|numeral 26|
#      m|C0450406|pH pattern|G/P|D003710|Demography
#      Removing Demography MH: C0450406|pH pattern|
#
#
# /* Remove extraneous Systematized Nomenclature of
#     Medicine entries.  Remove unless the concept contains
#     "SNOMED" or "Systematized Nomenclature of
#     Medicine"
#*/
#
#Removing SNOMED: CUI: C0450407 (ph+)  MH: Systematized Nomenclature of 
#Medicine  #MHs: 1
#
#
#/* Remove extraneous "Subject Headings" entries.  Remove
#    unless concept contains "Subject Heading".
#*/
#
#Removing Subject Heading: CUI: C0450411 (Forwards to the left)  MH: 
#Subject Headings  #MHs: 1
#
#
#/* Remove extraneous Logical Observation Identifiers Names and Codes 
#entries.
#    Remove unless the concept contains "LOINC", "identifier", 
#"Identifier", or
#    "Logical Observation Identifiers Names and Codes".
#*/
#
#Removing LOINC: CUI: C0484421 (Dohle body:Arbitrary Concentration:Point 
#in time:Whole blood:Ordinal:Microscopy.light)  MH: Logical Observation 
#Identifiers Names and Codes  #MHs: 4
#
#
#/* Remove extraneous Logical Observation Identifiers Names and Codes 
#entries.
#    Special case of ":identifier:" in strings not captured above.  So, 
#if the concept
#    contains either ":identifier:" or ":Identifier:", remove the LOINC MH.
#*/
#
#Removing LOINC: CUI: C2361061 (Diagnosis.addressed by 
#plan:Identifier:Point in time:Psychiatric rehabilitation 
#treatment:Nominal)  MH: Logical Observation Identifiers Names and Codes  
##MHs: 3
#
#
#/* Remove "Carcinoma" entries whenever concept has  the word "Cancer"
#    or "cancer".
#*/
#
#Removing Carcinoma: CUI: C0278486 (Breast cancer stage II)  MH: 
#Carcinoma  #MHs: 2
#
#
#/* Remove extraneous Family History entries
#     -- Remove "Family" MeSH Heading from entries with  "FH: ", "fh: ", 
#"FH ",
#         "Family history", "no fh", or " family history".
#*/
#
#Removing Family: CUI: C0332123 (No family history of)  MH: Family  #MHs: 5
#
#
#/* Remove extraneous International System of Units entries.  Remove
#    the MH from any concept that doesn't have at least one of the following
#    "Unit", "unit", "Measurement", or "measurement".
#*/
#
#Removing ISU: CUI: C0439209 (Kilogram)  MH: International System of 
#Units  #MHs: 1
#

#usable test script:
#umls_concept_data_filename='/Users/jherskovic/Projects/MEDRank2/data/umls_concepts_2009_AB.db'
#from MEDRank.umls.concept import Concept
#from MEDRank.umls.restrict_to_mesh_converter import RestrictToMeSHConverter
#from MEDRank.file.disk_backed_dict import StringDBDict
#from MEDRank.mesh.tree import Tree
#Concept.init_storage(StringDBDict(umls_concept_data_filename))
#t=Tree()
#c=RestrictToMeSHConverter(t)
#x=Concept('C0484421')
#c.convert(x)
# #Should return  <Expression: [<MeSH term microscopy () []>, <MeSH term blood () []>]>
#c.convert(Concept('C0278486'))
# #Should return <Expression: [<MeSH term breast neoplasms () []>]>

import sys
import os
import unittest
from MEDRank.umls.converter import Converter
from MEDRank.mesh.expression import Expression
from MEDRank.mesh.term import Term

INCLUDE_EVERYTHING="MAGICAL_TOKEN_TO_INCLUDE_EVERYTHING!"

class RestrictToMeSHConverter(Converter):
    """RestrictToMeSHConverter is based on the Converter class. It applies only 
    the RestrictToMeSH algorithm, without any extra rules.
    """
    exclusions=set(['C0439067', 'C0439068', 'C0439069', 'C0439070', 'C0445385', 
                    'C0450340', 'C0450349', 'C0450406'])
    # The 'bad mhs' list includes tuples that contain bad MeSH headings and the
    # conditions under which they should be included (i.e. when the concept name
    # matches one of the first members in the tuple), except when they 
    # shouldn't (match the second member of the tuple)
    bad_mhs={'demography': (set(['demography']), set()),
             'systematized nomenclature of medicine': 
                (set(['systematized nomenclature of medicine',
                      'snomed',
                      'snomed ct'
                     ]),
                 set()),
             'subject headings': (set(['subject heading']), set()),
             'logical observation identifiers names and codes':
                (set(['loinc',
                      'identifier',
                      'logical observation identifiers names and codes'
                     ]),
                 set([':identifier:'])),
             'carcinoma': (INCLUDE_EVERYTHING, set(['cancer'])),
             'family': (set(['fh:',
                             'fh ',
                             'family history',
                             'no fh'
                            ]),
                        set()),
             'international system of units': (set(['unit',
                                                    'measurement'
                                                   ]),
                                               set()),
            }
    def __init__(self, tree, rule_data=None, skip_unknown_concepts=True):
        Converter.__init__(self, tree, rule_data, skip_unknown_concepts,
                            set(['a', 'i', 'g/p', 'g/s', 'g/c', 'o']))
    def check_checktag_rules(self, CUI):
        return
    def check_extra_checktag_rules(self, an_expression):
        return
    def check_for_subheadings(self, an_expression):
        return []
    def check_for_exclusion(self, CUI):
        return CUI.upper() in self.exclusions
    def convert_step_2(self, umls_concept):
        return Expression([Term(x) for x in 
                           umls_concept.names_and_ids.itervalues()])
    def convert(self, umls_concept):
        """Performs an extra pass through the bad_mhs rules"""
        tentative_conversion=Converter.convert(self, umls_concept)
        new_conversion=[]
        for mh in tentative_conversion.utterance:
            mh_ls=mh.term.lower().strip() 
            if mh_ls not in self.bad_mhs:
                new_conversion.append(mh)
            else:
                # Exclusions first, to deal with 'carcinoma'
                exclusions=self.bad_mhs[mh_ls][1]
                inclusions=self.bad_mhs[mh_ls][0]
                exclusion_triggered=False
                for e in exclusions:
                    if e in umls_concept.concept_name:
                        exclusion_triggered=True
                        break
                if inclusions==INCLUDE_EVERYTHING:
                    if not exclusion_triggered:
                        new_conversion.append(mh)
                    continue
                for i in inclusions:
                    if i in umls_concept.concept_name:
                        if not exclusion_triggered:
                            new_conversion.append(mh)
                        continue
        return Expression(new_conversion)
        