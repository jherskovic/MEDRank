#!/usr/bin/env python
# encoding: utf-8
"""
metamap_machine_output.py
Handles machine output from METAMAP; turns a METAMAP file into a nice set of chunked linelists (see nlm_output.py).

The line parsers are quite intolerant, and throw exceptions on all malformed
lines. The document parser tolerates the ones that aren't likely to impact
parsing quality (i.e. no line id, because it means that there was an error
message in the code or something similar).

Since METAMAP machine output lines DO NOT have line IDs, this set of classes 
remembers the last seen ID and returns that for lines that don't have one.
NOTE: THIS MEANS THAT THESE CLASSES ARE NOT THREAD-SAFE!

Requires pyparsing, in order to parse the (*&#&%^$™@) output lines properly.
Regular expressions just don't cut it.

Created by Jorge Herskovic on 2008-05-13.
Copyright (c) 2008 University of Texas - Houston. All rights reserved.
"""

import re
import operator
from MEDRank.utility.logger import logging, ULTRADEBUG
from MEDRank.file.nlm_output import (ChunkedNLMOutput,
                                     CUINotFoundError, ParsingError,
                                     NoConfidenceError,
                                     NoLineIDError,
                                     LineList)
from pyparsing import *

# These lines are known to be useless to the parser. We have gathered them 
# here for the user's convenience.
# pylint: disable-msg=C0103
DEFAULT_LINES_TO_IGNORE=[]

#
# PLEASE DO NOT TOUCH THE PARSER CODE UNLESS YOU ARE BLOODY WELL SURE OF
# WHAT YOU ARE DOING
#
# YES, THIS APPLIES TO MYSELF TOO!!!!! THERE ARE _A LOT_ OF SUBTLETIES
#

# This parser is based on pyparsing. It looks sort of awful, but is derived
# directly from the Mapping Info at the SKR site 
# (see http://skr.nlm.nih.gov/Help/Mapping_Info.html for documentation)
number=Word("0123456789")
candidate_score=Suppress(Optional("-")) + number.setResultsName("Score")
umls_concept_id=Combine(oneOf("c C")+number).setResultsName("ConceptID")
#quoted_concept_name=Suppress("'")+\
#             Word(alphanums+" ?-+=_()[],.:;*&^%$#@\"!<>{}/")+\
#             Suppress("'")
# The following can swallow apostrophes in a concept name
# And handle closing double apostrophes (ugh, they should really just escape
# those characters!)
dastardly_quote_including_concept_name=Suppress("'")+\
            Combine(ZeroOrMore("''")+\
            Word(alphanums+" ?-+=_()[],.:;*&^%$#@\"!<>{}/")+\
            ZeroOrMore(OneOrMore("''")+\
            Word(alphanums+" ?-+=_()[],.:;*&^%$#@\"!<>{}/"))+\
            ZeroOrMore("''"))+\
            Suppress("'")
unquoted_concept_name=(Word(alphanums+'-?_+=()') | alphanums)
#concept_name=(quoted_concept_name | unquoted_concept_name)
concept_name=(dastardly_quote_including_concept_name | unquoted_concept_name)
semantic_type=Suppress(Optional("'"))+\
              Word(alphas).setResultsName('SemanticType')+\
              Suppress(Optional("'"))
one_match=Suppress("[[")+\
          Word(nums).setResultsName("PhraseWordSpanBegin")+\
          Suppress(",")+\
          Word(nums).setResultsName("PhraseWordSpanEnd")+\
          Suppress("],[")+\
          Word(nums).setResultsName("ConceptWordSpanBegin")+\
          Suppress(",")+\
          Word(nums).setResultsName("ConceptWordSpanEnd")+\
          Suppress("],")+\
          Word(nums).setResultsName("Variation")+\
          Suppress("]")
match_map=Suppress("[")+Group(Optional(one_match)+ZeroOrMore(Suppress(",")\
          +one_match))+Suppress("]")
ev=Suppress("ev(")+\
   Group(\
   candidate_score+\
   Suppress(",'")+\
   umls_concept_id+\
   Suppress("',")+\
   concept_name.setResultsName("Name")+\
   Suppress(",")+\
   concept_name.setResultsName("Description")+\
   Suppress(",[")+\
   Group(Optional(concept_name)+
         ZeroOrMore(Suppress(",")+concept_name)).setResultsName("Matched")+\
   Suppress("],[")+\
   Group(Optional(semantic_type)+
         ZeroOrMore(Suppress(",")+semantic_type)).setResultsName("Types")+\
   Suppress("],")+\
   match_map.setResultsName("MatchMap")+\
   Suppress(",")+\
   oneOf("yes no").setResultsName("HeadOfPhrase")+\
   Suppress(",")+\
   oneOf("yes no").setResultsName("Overmatch")\
   )+\
   Suppress(")")
ev_expressions=Suppress("[")+Group(Optional(ev)+\
               ZeroOrMore(Suppress(",")+ev))+\
               Suppress("]")
map_expression=Suppress("map(")+\
               Group(candidate_score+\
               Suppress(",")+\
               ev_expressions.setResultsName("Expression"))+\
               Suppress(")")
map_expressions=Suppress("[") + Group(Optional(map_expression) + \
                ZeroOrMore(Suppress(",") + map_expression)) + Suppress("]")
mappings=Suppress("mappings(") + map_expressions + Suppress(").")

class WrongTypeOfLineError(ParsingError):
    """Represents that the line passed to the line parser is of the wrong type
    """
    pass
    
# We can't use most of the Line infrastructure for this... so we will have to
# create another, parallel one.
class MachineOutputLine(object):
    """Represent a line in a METAMAP Machine output file."""
    slots=['_line', '_line_type']
    _line_id=None
    def __init__(self, original_line):
        self._line=original_line.strip().lower()
        self._line_type=self._line.split('(')[0]
    # The line property.
    def line_fget(self):
        "Getter for the line property"
        return self._line
    line=property(line_fget)
    # The line_type property.
    def line_type_fget(self):
        "Getter for the line_type property"
        return self._line_type
    line_type=property(line_type_fget)
    def get_line_id(self):
        return MachineOutputLine._line_id
    line_id=property(get_line_id)
    
class UtteranceLine(MachineOutputLine):
    """Parses an Utterance Line"""
    __slots__=['_my_line_id']
    parser=re.compile(r'utterance\(\'(?P<id>.*?)\',\"(?P<sentence>.*?)\"\)\.',
                      re.IGNORECASE)
    numbers=re.compile(r'\d+')
    def __init__(self, original_line):
        MachineOutputLine.__init__(self, original_line)
        if self.line_type!='utterance':
            raise WrongTypeOfLineError("%r is not an utterance." % self.line)
        parsed_line=UtteranceLine.parser.match(self.line).groupdict()
        self._my_line_id=int(
            UtteranceLine.numbers.findall(parsed_line['id'])[0])
        logging.log(ULTRADEBUG, "Created an UtteranceLine with set id %d",
                      self._my_line_id)
        # Update the line id for this lexer
        MachineOutputLine._line_id=self._my_line_id
    # The line_id property.
    def __repr__(self):
        return "<UtteranceLine %d @ %#x>" % (self.line_id, id(self))
        
class EndOfUtteranceLine(MachineOutputLine):
    """Represents the end of an utterance."""
    def __init__(self, original_line):
        MachineOutputLine.__init__(self, original_line)
        if self.line_type!="'eou'.":
            raise WrongTypeOfLineError("%r is not an end of utterance." %
                                       self.line)
    def __repr__(self):
        return "<EndOfUtteranceLine @ %#x>" % (id(self))
        
class CandidateLine(MachineOutputLine):
    """Candidate lines - we're not using this one right now, so we just skip
    them."""
    def __init__(self, original_line):
        MachineOutputLine.__init__(self, original_line)
        if self.line_type!='candidates':
            raise WrongTypeOfLineError("%r is not a candidates line." %
                                       self.line)
    def __repr__(self):
        return "<CandidateLine @ %#x>" % id(self)

class PhraseLine(MachineOutputLine):
    """Phrase Lines - not useful for our purposes"""
    def __init__(self, original_line):
        MachineOutputLine.__init__(self, original_line)
        if self.line_type!='phrase':
            raise WrongTypeOfLineError("%r is not a phrase line." %
                                       self.line)
    def __repr__(self):
        return "<PhraseLine @ %#x>" % id(self)

class ConceptLine(MachineOutputLine):
    """Not a real line from the file, represents a decomposed MappingLine"""
    __slots__=['_cui', '_description', '_confidence']
    def __init__(self, cui, description, confidence):
        MachineOutputLine.__init__(self, '()') # There's no real equivalent
        self._cui=cui
        self._description=description
        self._confidence=confidence
    def cui_get(self):
        return self._cui
    CUI=property(cui_get)
    def description_get(self):
        return self._description
    description=property(description_get)
    def confidence_get(self):
        return self._confidence
    confidence=property(confidence_get)
    def __repr__(self):
        return "<ConceptLine @ %#x for CUI %s (%s)>" % (id(self),
                                                        self.CUI,
                                                        self.description)
class MappingLine(MachineOutputLine):
    """A mapping line - these are the ones we're actually interested in. Due
    to the syntax of machine output files, these will have to be told what 
    their ID is."""
    #map_parser=re.compile(r"""map\((?P<map_score>\-?\d+?)\,
    #                          \[(?P<the_rest>.*)\]\)\.""", re.VERBOSE |
    #                                                       re.IGNORECASE)
    ## We're only really interested in matching EVs
    #ev_parser=re.compile(r"""ev\((?P<candidate_score>\-?\d+?)\,
    #                      \'(?P<cui>c\d+)\'\,
    #                      \'?(?P<umls_concept>.+?)\'?\,
    #                      \'?(?P<preferred_concept_name>.+?)\'?\,
    #                      \[(?P<matched_words>.*?)\]\, 
    #                      \[(?P<semantic_types>.*?)\]\, 
    #                      \[(?P<match_positions>.*?)\]\,[yes|no]
    #                      """, re.VERBOSE | re.IGNORECASE)
    #                      # Ignore the rest of the string
    #                      # \)\])\]\)\.""")
    #position_extractor=re.compile(r"""\[\[(\d+)\,""")
    def __init__(self, original_line):
        MachineOutputLine.__init__(self, original_line)
        if self.line_type!='mappings':
            raise WrongTypeOfLineError("%r is not a mappings line." %
                                       self.line)                                   
        logging.log(ULTRADEBUG, "Created a MappingLine")
    def iter_concepts(self):
        """Iterates through the concepts (only one per position) so that
        they can be extracted in order. We will get the first concept that
        covers each positional 'slot' in the original. """
        #concepts_iter=MappingLine.ev_parser.finditer(self.line)
        #concept_slots={}
        #for concept in concepts_iter:
        #    concept=concept.groupdict()
        #    positions=MappingLine.position_extractor.findall(
        #            concept['match_positions'])
        #    this_pos=int(positions[0])
        #    covered_pos=reduce(operator.or_, [int(x) in concept_slots for x in
        #                                      positions])
        #    if covered_pos in concept_slots:
        #        continue
        #    concept_slots[this_pos]=ConceptLine(concept['cui'], 
        #                             concept['preferred_concept_name'],
        #                             -int(concept['candidate_score']))
        #    # Fill in the rest of the slots covered by this concept
        #    for each_slot in positions[1:]:
        #        concept_slots[int(each_slot)]=None
        #        
        #ordered_slots=concept_slots.keys()
        #ordered_slots.sort()
        #for slot in ordered_slots:
        #    if concept_slots[slot] is not None:
        #        yield concept_slots[slot]
        #return
        try:
            all_mappings=mappings.parseString(self.line)[0]
        except:
            logging.warn("FAIL parsing %s", self.line)
            raise
        if len(all_mappings)==0:
            return
        # Get the mapping with the best score. If all have the same score,
        # uses the first one.
        best_mapping=all_mappings[0]['Expression'][0]
        best_mapping_score=all_mappings[0]['Score']
        for m in all_mappings[1:]:
            if m['Score']>best_mapping_score:
                best_mapping_score=m['Score']
                best_mapping=m['Expression'][0]
        # The EVs are in order
        for e in best_mapping:
            new_concept=ConceptLine(e['ConceptID'],
                                    e['Name'],
                                    int(e['Score']))
            logging.debug("Emitting %r", new_concept)
            yield new_concept
        return
        
def line_factory(line_text):
    """Builds a line of the appropriate type by trial and error."""
    line_types_to_try=[UtteranceLine, MappingLine, EndOfUtteranceLine,
                       CandidateLine, PhraseLine]
    for t in line_types_to_try:
        try:
            tentative_line=t(line_text)
        except WrongTypeOfLineError:
            tentative_line=None
        else:
            break
    if tentative_line is None:
        raise WrongTypeOfLineError("%s is not of one of the known Metamap "
                                   "machine output line types." % line_text)
    return tentative_line
    
class MetamapMachineOutput(ChunkedNLMOutput):
    """Represents a Metamap Machine output file that contains chunked data
    from several articles simultaneously. It iterates through the file one
    article at a time."""
    def __init__(self, fileobject, lines_to_ignore, chunkmap):
        ChunkedNLMOutput.__init__(self, fileobject,
                                    type_of_lines=line_factory,
                                    lines_to_ignore=lines_to_ignore,
                                    chunkmap=chunkmap)
    def ignore_exception(self, which_exception, on_which_line):
        """Decides whether exceptions during parsing correspond to known
        problems with SEMREP's output, and whether to ignore the corresponding 
        lines."""
        if type(which_exception) is WrongTypeOfLineError:
            logging.log(ULTRADEBUG, "Skipping line '%s' because its type could not be "
                          "determined.", on_which_line)
            return True
        return False
    def __iter__(self):
        """We need to build on the previous iterator because each MappingLine
        (that ChunkedNLMOutput will return) actually contains several concepts
        that must be separated. We will separate those components into 
        MetamapLine."""
        for lineset in ChunkedNLMOutput.__iter__(self):
            # Get a line list, turn MappingLines into ConceptLines, repackage
            new_lines=[]
            for line in lineset.lines:
                if isinstance(line, MappingLine):
                    for concept in line.iter_concepts():
                        new_lines.append(concept)
                else:
                    new_lines.append(line)
            yield LineList(lineset.set_id, new_lines)
        return


# Creating graphs should be the responsibility of other classes
# NOT of the input parsers, so if this parser only creates entities,
# so be it

    
