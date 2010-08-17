#!/usr/bin/env python
# encoding: utf-8
"""
concrete_concept.py

Contains the actual data associated with a UMLS concept in the MEDRank system.
At the very least it contains the mappings to MeSH, as provided by Olivier
Bodenreider (see documentation in 
             preprocessing_scripts/build_concept_data_file.py):

It also contains the semantic types of each concept.

Created by Jorge Herskovic on 2008-05-12.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""
# Disable warnings about spaces before operators (they drive me crazy)
# pylint: disable-msg=C0322
# Don't complain about the number of arguments to __init__
# pylint: disable-msg=R0913

from MEDRank.utility.logger import logging, ULTRADEBUG
from MEDRank.umls.names_and_ids import NamesAndIDs 

class ConcreteConcept(object):
    """Contains all of the information about a UMLS concept MEDRank cares
    about, including how to map it to MeSH. """
    __slots__=["__cn", # Preferred concept name
               "__mm", # Mapping method
               "__ni", # Names and IDs
               "__st"  # Semantic types
               ] 
    def __init__(self, name, method, names, identifiers, semtypes):
        self.__cn=name
        self.__mm=method
        self.__ni=NamesAndIDs(names, identifiers)
        self.__st=semtypes
        logging.log(ULTRADEBUG, "Creating ConcreteConcept %r", self)
    def __repr__(self):
        return "<ConcreteConcept %s>" % self.__cn
    def get_concept_name(self):
        "Concept name getter"
        return self.__cn
    concept_name=property(get_concept_name)
    def get_mapping_method(self):
        "Mapping method getter"
        return self.__mm
    mapping_method=property(get_mapping_method)
    def get_names_and_ids(self):
        "Names and IDs getter"
        return self.__ni
    names_and_ids=property(get_names_and_ids)
    def is_mapped(self):
        "Is this concept actually mapped?"
        # If there are names and IDs, it is mapped. If not, it isn't.
        return len(self.__ni)>0
    def get_semantic_types(self):
        """Getter for semantic_types"""
        return self.__st
    semantic_types=property(get_semantic_types)
    def __getstate__(self):
        return {'n': self.__cn, 'm': self.__mm, 'i': self.__ni, 
                's': self.__st}
    def __setstate__(self, state):
        self.__cn=state['n']
        self.__mm=state['m']
        self.__ni=state['i']
        self.__st=state['s']
        