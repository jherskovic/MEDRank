#!/usr/bin/env python
# encoding: utf-8
"""
term.py

Created by Jorge Herskovic on 2008-04-22.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

class Term(object):
    """Describes a MeSH term. A MeSH term is a unique term that is part of the
    MeSH vocabulary. It can also have a "role": a qualifier, a checktag, a
    MeSH heading, a subheading. The role should be assigned by the creator.
    Once created, the term and role cannot be changed.
    The role and the term and cleaned up (lowercased, stripped) upon
    instantiation. Comparison is allowed, and checks for equivalence of the
    terms."""
    __slots__=['__term', '__role', '__synonyms']
    def __init__(self, term, role='', synonyms=[]):
        self.__term=term.strip().lower()
        self.__role=role.strip().lower()
        self.__synonyms=[x.strip().lower() for x in synonyms]
    def __repr__(self):
        return "<MeSH term %s (%s) %r>" % (self.__term, self.__role, self.__synonyms)
    def __eq__(self, other):
        return self.term==other.term
    def get_term(self):
        "Getter for the term"
        return self.__term
    term=property(get_term)
    def get_role(self):
        "Getter for the role"
        return self.__role
    role=property(get_role)
    def get_synonyms(self):
        return self.__synonyms[:] # Protective copy
    synonyms=property(get_synonyms)
    def __getstate__(self):
        return {'t': self.__term, 'r': self.__role, 's': self.__synonyms}
    def __setstate__(self, state):
        self.__term=state['t']
        self.__role=state['r']
        try:
            self.__synonyms=state['s']
        except KeyError:
            self.__synonyms=[]
    def __hash__(self):
        return hash(self.__term)