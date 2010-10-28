#!/usr/bin/env python
# encoding: utf-8
"""
expression.py

Created by Jorge Herskovic on 2008-05-19.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import operator
from MEDRank.mesh.term import Term

class Expression(object):
    """Represents a MeSH expression, which can consist of one or more MeSH
    terms but is handled as a single unit. If the utterance is a single term
    it will be converted to a list.
    
    Expression contents should be Terms"""
    def __init__(self, utterance=[]):
        if isinstance(utterance, list):
            self._utterance=utterance
        else:
            self._utterance=[utterance]
        self._original_utterance=utterance
    def __repr__(self):
        return "<%s: %r>" % (self.__class__.__name__, self._utterance)
    # The utterance property.
    def utterance_fget(self):
        "Getter for the utterance property"
        return self._utterance
    def utterance_fset(self, value):
        "Setter for the utterance property"
        if isinstance(value, list):
            self._utterance=value
        else:
            self._utterance=[value]
        self._original_utterance=value
    utterance=property(utterance_fget, utterance_fset)
    def original_utterance_fget(self):
        return self._original_utterance
    original_utterance=property(original_utterance_fget)
    @staticmethod
    def _hash_function(x, y):
        return (hash(x) << 1) ^ hash(y)
    def __hash__(self):
        # self._utterance is always a list, which is unhashable
        if len(self._utterance)==0:
            return hash(0)
        the_hash=reduce(self._hash_function, 
                        (hash(x) for x in self._utterance))
        return the_hash
    def __eq__(self, other):
        return self._utterance==other._utterance
    def from_medline(self, medline_string):
        """Reformats a MEDLINE record headings field into an Expression by
        splitting across / lowercasing and removing stars. Also assigns the
        role of '*' to starred terms."""
        self._utterance=[Term(x, '*' if '*' in x else "") for x in 
                         medline_string.strip().replace('*',"").split('/')]
        self._original_utterance=medline_string
        return self # For method chaining
    def major_heading(self):
        """Returns a Major Heading if there is one; otherwise, returns 
        nothing"""
        if isinstance(self._original_utterance, list):
            potential_terms=self._original_utterance
        else:
            potential_terms=[x for x in 
                             self._original_utterance.strip().split('/')]
        potential_terms=[Term(x.replace('*', ''), '*' if '*' in x else "")
                         for x in potential_terms
                         if '*' in x]
        return potential_terms

class ExpressionList(list):
    """A list whose members are Expressions and that ignores empty Expressions
    when added."""
    def append(self, item):
        """Add a new, non-empty expression to the ExpressionList."""
        if len(item.utterance)>0:
            list.append(self, item)
        return
    def from_medline(self, medline_list):
        """Creates an expression list from a MEDLINE record list (usually the
        MeSH headings)"""
        for x in medline_list:
            self.append(Expression().from_medline(x))
        return self # for chaining
    @staticmethod
    def _hash_function(x, y):
        return (hash(x) << 1) ^ hash(y)
    def __hash__(self):
        # self._utterance is always a list, which is unhashable
        if len(self)==0:
            return hash(0)
        the_hash=reduce(self._hash_function, 
                        (hash(x) for x in self))
        return the_hash
    def flatten(self):
        """Renders the expression list as a simple string list (useful for
        evaluating). It will also disregard multiple copies of the same
        expression. Sometimes UMLS conversion can return several instances of
        the same term.
        """
        # NOTE: What if I want to use the fact that a MeSH term comes up more
        # than once to boost it? I'd have to redesign the conversion pipeline
        # to convert keeping scores, THEN merge the terms considering scores,
        # then cut off the lowest ones. Doable, but not in this design. I may
        # want to check and see if it's a problem later. 
        flat=set([])
        for expr in self:
            flat|=set([x.term for x in expr.utterance])
        return [x for x in flat]
    def major_headings(self):
        flat=set([])
        for expr in self:
            flat|=set([x.term for x in expr.major_heading()])
        return [x for x in flat]

# Do not use the following procedures!
def compare_flat_lists(flat_1, flat_2, tree):
    terms_1=[tree.search(x) for x in flat_1]
    terms_2=[tree.search(x) for x in flat_2]
    matchterms=[]
    for x in xrange(len(terms_1)):
        for y in xrange(len(terms_2)):
            if terms_1[x].any_matches(terms_2[y]):
                matchterms.append((x, y))
    match=[flat_1[x[0]] for x in matchterms]
    not_match_1=set([flat_1[x] for x in xrange(len(flat_1)) 
                     if x not in [y[0] for y in matchterms]])
    not_match_2=set([flat_2[x] for x in xrange(len(flat_2))
                     if x not in [y[1] for y in matchterms]])
    not_match_1=list(not_match_1)
    not_match_2=list(not_match_2)
    return (match, not_match_1, not_match_2)
    
def compare_lists(list_1, list_2, tree):
    """Compares two ExpressionLists by flattening them and using the MeSH
    terms' synonyms list to determine whether the contents refer to the same
    items or not. It turns out that MTI and MEDLINE might return synonyms, i.e.
    one might say "breast cancer" while the other says "breast neoplasms".
    That makes this kind of comparison necessary.
    
    Takes two lists and a MeSH tree. Returns a tuple with:
    (identical items, unmatched items from list 1, unmatched items from list 2)
    """
    flat_1=list_1.flatten()
    flat_2=list_2.flatten()
    return compare_flat_lists(flat_1, flat_2, tree)