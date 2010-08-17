#!/usr/bin/env python
# encoding: utf-8
"""
semrep.py

Handles output from SEMREP; turns a SEMREP file into a nice set of chunked
linelists (see nlm_output.py).

The line parsers are quite intolerant, and throw exceptions on all malformed
lines. The document parser tolerates the ones that aren't likely to impact
parsing quality (i.e. no line id, because it means that there was an error 
message in the code or something similar) 

Created by Jorge Herskovic on 2008-05-13.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""


from MEDRank.utility.logger import logging, ULTRADEBUG
from MEDRank.file.nlm_output import (Line, ChunkedNLMOutput,
                        CUINotFoundError, ParsingError,
                        NoConfidenceError,
                        NoLineIDError,
                        UnknownLineTypeError,
                        NoLineTypeError)
import re

# These lines are known to be useless to the parser. We have gathered them 
# here for the user's convenience.
# pylint: disable-msg=C0103
DEFAULT_LINES_TO_IGNORE=["semrep wrapper error"]

class SemrepLine(Line):
    """The basic semrep line has the ID in the second position instead of
    the first, so this class calls the constructor appropriately."""
    def __init__(self, original_line):
        Line.__init__(self, original_line, id_position=1, 
                      id_decorator_remover=lambda x: [x])
        
class EntityLine(SemrepLine):
    """Represents a line holding an Entity in the SEMREP output."""
    __slots__=['_cui', '_semantic_type', '_description']
    def __init__(self, original_line, 
                 cui_position=6, # Support for different SEMREP output formats
                 description_position=7,
                 semantic_type_position=8):
        SemrepLine.__init__(self, original_line)
        #line_breakup=self._line.split(self.split_char)
        try:
            self._cui=self.split_line[cui_position]
        except IndexError:
            raise CUINotFoundError("There was no CUI in the line '%s'" % 
                                   self._line)
        if self._cui=='':
            raise CUINotFoundError("There was no CUI in the line '%s'" % 
                                   self._line)
        try:
            self._description=self.split_line[description_position]
            self._semantic_type=self.split_line[semantic_type_position]
        except IndexError:
            raise ParsingError("Data missing from line '%s'" % self._line)
        # Some entities have no stated confidence. We use 0 in such cases,
        # so they can be eliminated from the workflow later.
        try:
            self.confidence=float(self.split_line[-3])/1000.0
        except ValueError:
            raise NoConfidenceError("Could not parse a confidence value in "
                                    "line '%s'" % self._line)
        logging.log(ULTRADEBUG, "Created an entity_line @ %d: %s (%s) %1.3f", 
                      self.line_id, self._cui,
                      self._description, self.confidence)
    # The CUI property.
    def cui_fget(self):
        "Getter for the cui property"
        return self._cui
    CUI=property(cui_fget)
    # The semantic_type property.
    def semantic_type_fget(self):
        "Getter for the semantic_type property"
        return self._semantic_type
    semantic_type=property(semantic_type_fget)
    # The description property.
    def description_fget(self):
        "Getter for the description property"
        return self._description
    description=property(description_fget)

class EntityLine07(EntityLine):
    """Represents an EntityLine as outputted by '07 SEMREPP"""
    def __init__(self, original_line):
        EntityLine.__init__(self, original_line, 8, 6, 7)

class RelationLine(SemrepLine):
    """Represents a line holding a Relationship in the SEMREP output."""
    __slots__=['_cui1', '_cui2', '_relation_type']
    def __init__(self, original_line):
        SemrepLine.__init__(self, original_line)
        #line_breakup=self._line.split(self.split_char)
        try:
            self._cui1=self.split_line[11]
            if self._cui1=='':
                raise IndexError() # Trigger the CUINotFoundError
        except IndexError:
            raise CUINotFoundError("There was no CUI1 in the line '%s'" % 
                                   self._line)
        try:
            self._cui2=self.split_line[33]
            if self._cui2=='':
                raise IndexError() # Trigger the CUINotFoundError
        except IndexError:
            raise CUINotFoundError("There was no CUI2 in the line '%s'" % 
                                   self._line)
        try:
            self._relation_type=self.split_line[24]
        except IndexError:
            raise ParsingError("Data missing from line '%s'" % self._line)
        
        try:
            self.confidence=float(self.split_line[-3])/1000.0
        except ValueError:
            raise NoConfidenceError("Could not parse a confidence value in "
                                    "line '%s'" % self._line)
        logging.log(ULTRADEBUG, "Created a relation_line @ %d: %s--%s-->%s (%1.3f)", 
                      self.line_id, self._cui1, self._relation_type,
                      self._cui2, self.confidence)
    # The cui1 property.
    def cui1_fget(self):
        "Getter for the cui1 property"
        return self._cui1
    CUI1=property(cui1_fget)
    # The cui2 property.
    def cui2_fget(self):
        "Getter for the cui2 property"
        return self._cui2
    CUI2=property(cui2_fget)
    # The relation_type property.
    def relation_type_fget(self):
        "Getter for the relation_type property"
        return self._relation_type
    relation_type=property(relation_type_fget)
    
class TextLine(SemrepLine):
    """SEMREP also returns lines holding the original text. We're not
    particularly interested in these right now."""
    pass
    
class SemrepOutput(ChunkedNLMOutput):
    """Represents a SEMREP output file that contains chunked data from several
    articles simultaneously. It iterates through the file one article at a
    time."""
    # _dispatch_table={'entity': EntityLine,
    #                     'relation': RelationLine,
    #                 'text': TextLine
    #                 }
    def __init__(self, fileobject, lines_to_ignore, chunkmap):
        ChunkedNLMOutput.__init__(self, fileobject,
                                    type_of_lines=SemrepOutput.line_factory,
                                    lines_to_ignore=lines_to_ignore,
                                    chunkmap=chunkmap)
    def ignore_exception(self, which_exception, on_which_line):
        """Decides whether exceptions during parsing correspond to known
        problems with SEMREP's output, and whether to ignore the corresponding 
        lines."""
        if type(which_exception) is CUINotFoundError:
            logging.log(ULTRADEBUG, "Skipping line '%s' because no CUI could be found "
                          "on it" % on_which_line)
            return True
        if type(which_exception) is NoLineTypeError:
            logging.log(ULTRADEBUG, "Skipping line '%s' because its type could not be "
                          "determined.", on_which_line)
            return True
        if type(which_exception) is NoConfidenceError:
            logging.log(ULTRADEBUG, "Skipping line '%s' because it has no confidence.",
                          on_which_line)
            return True
        if type(which_exception) is UnknownLineTypeError:
            logging.warn("Skipping line '%s' because it has an unknown type",
                          on_which_line)
            return True
        return False
    @staticmethod
    def line_factory(line_text):
        """Decides whether to instantiate an entity_line or a relation_line
        dynamically, so it can be passed to the chunked_nlm_output constructor
        instead of a type.

        In SEMREP output, the type of a line is its 6th element."""
        try:
            line_type=line_text.split('|')[5]
        except IndexError:
            raise NoLineTypeError("Could not determine the line type of '%s'",
                                  line_text)
        #try:
        #    return SemrepOutput._dispatch_table[line_type](line_text)
        if line_type=='entity':
            return EntityLine(line_text)
        if line_type=="relation":
            return RelationLine(line_text)
        if line_type=='text':
            return TextLine(line_text)
        #except KeyError:
        #    raise UnknownLineTypeError("Unknown line type in line '%s'" % 
        #                                line_text)
        raise UnknownLineTypeError("Unknown line type in line '%s'" % 
                                    line_text)
