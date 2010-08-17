#!/usr/bin/env python
# encoding: utf-8
"""
Converter.py

Represents a UMLS->MESH conversion algorithm.

Created by Jorge Herskovic on 2008-05-19.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import sys
import os.path
from MEDRank.utility.logger import logging, ULTRADEBUG
import cPickle as pickle
from MEDRank.umls.concept import NoConceptInfoError
from MEDRank.mesh.expression import Expression
from MEDRank.mesh.tree import TermNotInTree
from MEDRank.mesh.term import Term

_DEFAULT_CONVERTER_DATA=os.path.join(sys.exec_prefix, "medrank_data", 
                                     "mti_converter_data.p")

class ConverterError(Exception):
    """Base class for all converter exceptions."""
    pass

class ConverterStats(object):
    """Statistics for tracking and measuring the conversion process."""
    def __init__(self, known_stats):
        self._stats={}
        for stat in known_stats:
            self._stats[stat]=0
    def __repr__(self):
        return "<%s: %r>" % (self.__class__.__name__,   self._stats)
    # The stats property.
    def stats_fget(self):
        "Getter for the stats property"
        return self._stats
    stats=property(stats_fget)
    def __setitem__(self, key, value):
        self._stats[key]=value
    def __getitem__(self, key):
        return self._stats[key]
        
class ConverterData(object):
    """Holds static data necessary for the converter to operate."""
    def __init__(self, lists, checktag_rules, subheading_rules, extra_terms,
                 bad_terms):
        self._lists=lists
        self._checktag_rules=checktag_rules
        self._subheading_rules=subheading_rules
        self._extra_terms=extra_terms # This name is for historic reasons
        self._bad_terms=bad_terms
    def get_extra_checktag_rules(self):
        "Getter for extra terms"
        return self._extra_terms
    extra_checktag_rules=property(get_extra_checktag_rules)
    def get_lists(self):
        "Getter for lists"
        return self._lists
    lists=property(get_lists)
    def get_subheading_rules(self):
        "Getter for subheading_rules"
        return self._subheading_rules
    subheading_rules=property(get_subheading_rules)
    def get_checktag_rules(self):
        "Getter for checktag_rules"
        return self._checktag_rules
    checktag_rules=property(get_checktag_rules)
    def get_bad_terms(self):
        "Getter for bad terms"
        return self._bad_terms
    bad_terms=property(get_bad_terms)
    def get_known_checktags(self):
        "Getter for all known checktags"
        checktags=set([])
        for v in self.checktag_rules.itervalues():
            checktags|=set([x for x in v])
        return checktags
    known_checktags=property(get_known_checktags)
    def get_known_subheadings(self):
        sh=set([])
        for x in self.subheading_rules:
            sh|=set([t for t in x['terms']])
        return sh
    known_subheadings=property(get_known_subheadings)
    
#NOTE: I may need to rework the converter (or, more likely, add a wrapper 
#class) to keep scores. Scores are apparently relevant ;) and I may want to
# cut off AFTER converting ranking and  not before.
class Converter(object):
    """The basic UMLS->MeSH conversion algorithm. Uses only synonyms and 
    associated expressions, does not pass supplementary concepts, and returns
    MeSH expressions for every UMLS concept it receives.
    The converter requires a MeSH tree to work.
    
    The basic protocol is to call start_conversion, call convert as necessary,
    then call end_conversion. end_conversion will spit out a list of
    Expressions based on what was observed during the conversion process (i.e.
    extra checktags, etc.)"""
    def __init__(self, tree, rule_data=None, skip_unknown_concepts=True,
                 accepted_types=set(['a', 'i'])):
        logging.debug("Creating Converter with tree %r", tree)
        self._tree=tree
        if rule_data is None:
            rule_data=pickle.load(open(_DEFAULT_CONVERTER_DATA, "rb"))
            logging.info("Using converter data from %r", 
                         _DEFAULT_CONVERTER_DATA)
        self._data=rule_data
        self._extra_checktags=set() 
        self._skip_unknown=skip_unknown_concepts
        self._accepted_types=accepted_types
    def start_conversion(self):
        """start_conversion:
        Begin the conversion process by cleaning up the internal state of the
        converter."""
        if len(self._extra_checktags)>0:
            logging.warn("Cleaning up _extra_checktags, but there was content"
                         " there. Someone didn't retrieve it.")
        self._extra_checktags=set()
    def get_data(self):
        """Expose the converter data for other uses"""
        return self._data
    data=property(get_data)
    def convert_step_2(self, umls_concept):
        """Converts a UMLS concept into a MeSH expression."""
        if umls_concept.mapping_method not in self._accepted_types:
            # Unless there's only a single concept as a target
            if len(umls_concept.names_and_ids)==1:
                return Expression([Term(x) for x in 
                                   umls_concept.names_and_ids.itervalues()])
            else:
                #logging.debug("Concept %r has an unsupported mapping type", 
                #              umls_concept)
                return Expression([])
                #pass
        # Concepts mapped with mapping method "A" are associated expressions,
        # i.e. compound mappings
        if umls_concept.mapping_method=='a':
            return Expression([Term(x) for x in
                               umls_concept.names_and_ids.itervalues()])
        # Now only the synonyms remain. Is there just one item? Return it.
        if len(umls_concept.names_and_ids)==1:
            return Expression([Term(x) for x in
                              umls_concept.names_and_ids.itervalues()])
        # Is there just one descriptor? Return it.
        descriptors=[umls_concept.names_and_ids[x] for x in
                     umls_concept.names_and_ids.iter_descriptors()]
        if len(descriptors)==1:
            return Expression([Term(x) for x in descriptors])
        # Is there one descriptor identical to the name? Return the concept
        # name.
        if len([x for x in descriptors if x==umls_concept.concept_name])==1:
            return Expression([Term(umls_concept.concept_name)])
        # Do all qualifiers and descriptors share the same text?
        qualifiers=[umls_concept.names_and_ids[x] for x in
                    umls_concept.names_and_ids.iter_qualifiers()]
        unique_names=set(descriptors) | set(qualifiers)
        if len(unique_names)==1:
            # Return the only name
            return Expression(Term(unique_names.pop()))
        # I give up; return the deepest item according to the tree.
        tree_depths=[(self._tree[x].deepest_depth(), x) 
                     for x in umls_concept.names_and_ids.itervalues()]
        tree_depths.sort(reverse=True)
        deepest=self._tree.deepest_of_list(x for x in 
                                    umls_concept.names_and_ids.itervalues())
        return Expression([Term(deepest)]) # Return the term
        # Return all descriptors
        #return Expression([Term(umls_concept.names_and_ids[x]) 
        #                   for x in
        #                   umls_concept.names_and_ids.iter_descriptors()])
    def check_for_exclusion(self, CUI):
        """Checks to see if a term should be eliminated from the conversion
        workflow."""
        if '_exclusions' in self.data.lists: 
            return CUI in self.data.lists['_exclusions']
        else:
            return False
    def check_checktag_rules(self, CUI):
        """Compares a CUI to the checktag rules, and emits checktags if it
        matches. If a CUI is a member of an MTI list, and the list is a known
        match to a checktag, we emit the checktag at the end of the
        process."""
        # We check every list for membership (except exclusions)
        for (listname, checktags) in self.data.checktag_rules.iteritems():
            if listname=='_exclusions':
                continue
            if CUI in self.data.lists[listname]:
                logging.log(ULTRADEBUG, 'CUI %r matches list %r. Checktags %r added.',
                              CUI, listname, checktags)
                self._extra_checktags|=set([Term(x) for x in checktags])
    def check_extra_checktag_rules(self, an_expression):
        """Checks to see if a mesh term is in a known checktag-emitting
        tree"""
        positions=[self._tree[a_term.term].position for a_term in            
                   an_expression.utterance]
        for position in positions:
            for rule in self.data.extra_checktag_rules:
                """Check each position in each tree for membership in the
                tree-based checktag rules"""
                if 'in' in rule:
                    in_rule=any([any([x in y for x in rule['in']]) 
                                 for y in position])
                else:
                    in_rule=False
                if 'not in' in rule:
                    not_in_rule=any([any([x in y for x in rule['not in']])
                                     for y in position])
                else:
                    not_in_rule=False
                if in_rule and not not_in_rule:
                    logging.log(ULTRADEBUG, "Expression %r matches checktag rule %r",
                                  an_expression, rule)
                    self._extra_checktags|=set([Term(x) for x in 
                                                rule['terms']])
        return
    def check_for_subheadings(self, an_expression):
        "Checks to see if this expression needs a subheading added."
        positions=[self._tree[a_term.term].position for a_term in            
                   an_expression.utterance]
        for position in positions:
            for rule in self.data.subheading_rules:
                """Check each position in each tree for membership in the
                tree-based checktag rules"""
                if 'in' in rule:
                    in_rule=any([any([x in y for x in rule['in']]) 
                                 for y in position])
                else:
                    in_rule=False
                if 'not in' in rule:
                    not_in_rule=any([any([x in y for x in rule['not in']])
                                     for y in position])
                else:
                    not_in_rule=False
                if in_rule and not not_in_rule:
                    logging.log(ULTRADEBUG, "Expression %r matches subheading rule %r",
                                  an_expression, rule)
                    return [Term(x) for x in rule['terms']]
        return []
        
    def convert_step_1(self, umls_concept):
        """Performs the direct UMLS->MeSH conversion and applies extra
        rules."""
        if self.check_for_exclusion(umls_concept.CUI):
            # If a term should be excluded, end the process right now
            logging.log(ULTRADEBUG, "Concept %r matches exclusion", umls_concept)
            return Expression([])
        # Check for known checktags for this CUI
        self.check_checktag_rules(umls_concept.CUI)
        # Convert
        candidate=self.convert_step_2(umls_concept)
        # Omit known-bad terms
        candidate=Expression([x for x in candidate.utterance
                              if x.term not in self.data.bad_terms])
        if len(candidate.utterance)==0:
            # No sense in postprocessing an empty transformation
            logging.log(ULTRADEBUG, "Obtained empty utterance for concept %r", 
                          umls_concept)
            return candidate
        # Check for extra tree-based checktags
        self.check_extra_checktag_rules(candidate)
        # Check for subheadings
        subheadings=self.check_for_subheadings(candidate)
        candidate.utterance+=subheadings
        logging.log(ULTRADEBUG, 'Mapped %r to %r successfully', umls_concept, candidate)
        return candidate
    def convert(self, umls_concept):
        try:
            return self.convert_step_1(umls_concept)
        except NoConceptInfoError:
            if not self._skip_unknown:
                raise
            else:
                logging.debug("There is no detailed info on %r", umls_concept)
                return Expression([])
        except TermNotInTree:
            if not self._skip_unknown:
                raise
            else:
                logging.debug("I could not find an equivalence for %r "
                            "in the tree %r", 
                             umls_concept, self._tree)
                return Expression([])

    def end_conversion(self):
        """Returns checktags that accumulated during the conversion"""
        cts=Expression([x for x in self._extra_checktags])
        self._extra_checktags=set()
        return cts
     
