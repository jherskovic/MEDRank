#!/usr/bin/env python
# encoding: utf-8
"""
nlm_output.py

NLM output files are plain text files with certain common features: each line
has a confidence value, an ID carried over from input, and other data. We
define two parallel tracks of classes that interact: 
line (meant to be subclassed with more specific fields) and
nlm_output (meant to be subclassed for each NLM tool that wants to process
line-by-line output)

chunked_nlm_output (meant to be subclassed by tools that handle chunked
output), its iterator returns sets of lines from the same chunk.

NLM output files also have application-specific error lines that should be
ignored.

Created by Jorge Herskovic on 2008-05-13.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""
# Disable warnings about spaces before operators (they drive me crazy)
# pylint: disable-msg=C0322

from MEDRank.utility.logger import logging, ULTRADEBUG
import re
from MEDRank.file.text import Text
from MEDRank.pubmed.pmid import Pmid

class ParsingError(Exception):
    """A general parsing error."""
    pass
class NoLineIDError(ParsingError):
    """A line ID was not found (this usually means an error report from the
    NLM parser)"""
    pass

# Other useful types
class CUINotFoundError(ParsingError):
    """The parser could not find a CUI in a line that should have had one.
    Common causes are: that the line is too short, or that it didn't have a
    CUI (genetic sequences are guilty of this)"""
    pass
class NoConfidenceError(ParsingError):
    """The parser could not compute a confidence value for the line, either
    because it doesn't have one in the proper position or because the line is
    too short."""
    pass
class UnknownLineTypeError(ParsingError):
    """The parser couldn't figure out the type of line it was looking at."""
    pass
class NoLineTypeError(ParsingError):
    """The line has no type of line marker."""
    pass

class Line(object):
    """Represent a line in an NLM output file."""
    slots=['_id', '_line', '_confidence', '_split_char', 'split_line']
    number_parser=re.compile(r'\d+')
    def __init__(self, original_line, id_position=0, split_char='|', 
                 id_decorator_remover=number_parser.findall):
        """decorator_remover is a function that will reliably strip whatever
        comes attached to the id. It defaults to just taking anything that 
        looks like a number, via a regular expression.
        We will also keep split_line as a regular public member to save 
        literally millions of function calls.
        """
        # The line below is unnecessary - text lines are already stripped and
        # lowercased for processing
        #self._line=original_line.strip().lower()
        self._line=original_line
        self._split_char=split_char
        self.split_line=original_line.lower().split(split_char)
        # The ID is usually the first element on every line. It may have some
        # decoration, so we use a regular expression to extract it.
        try:
            self._id=int(id_decorator_remover(
                         self.split_line[id_position])[0])
        except (IndexError, ValueError):
            raise NoLineIDError("There is no integer ID at the specified of"
                                " the position(%d) of the line '%s'" % 
                                (id_position, self._line))
        self._confidence=0
    def get_id(self):
        "Getter for the line ID"
        return self._id
    line_id=property(get_id)
    # The confidence property.
    def confidence_fget(self):
        "Getter for the confidence property"
        return self._confidence
    def confidence_fset(self, value):
        "Setter for the confidence property"
        self._confidence=value
    confidence=property(confidence_fget, confidence_fset)
    def split_char_fget(self):
        "Setter for the split_char property"
        return self._split_char
    split_char=property(split_char_fget)
    def get_line(self):
        "Getter for the split_char property"
        return self._line[:]
    line=property(get_line)
    #def get_split_line(self):
    #    return self._split_line
    #split_line=property(get_split_line)
    
class LineList(object):
    """Represents a list of lines tied to the same article ID, probably by a
    chunkmap."""
    def __init__(self, set_id, lines):
        self._set_id=set_id
        self._lines=lines
    def get_set_id(self):
        "Getter for the set_id property"
        return self._set_id
    set_id=property(get_set_id)
    def lines(self):
        "Getter for the lines property"
        return self._lines
    lines=property(lines)
    def __repr__(self):
        return "<LineList object for %s>" % self.set_id
    
class NLMOutput(Text):
    """Represents an output file from a NLM program."""
    def __init__(self, fileobject, type_of_lines, lines_to_ignore):
        Text.__init__(self, fileobject)
        self.__line_type=type_of_lines
        # Since all files are lowercased and stripped, the lines to ignore
        # must be so, too.
        self.__lines_to_ignore=[x.lower().strip() for x in lines_to_ignore]
    def __repr__(self):
        return "<%s file based on %r>" % (self.__class__.__name__,
                                          Text.__repr__(self))
    def is_ignorable(self, which_line):
        """We need to specify ignorable lines in terms of useless strings,
        so we need to check the input against these."""
        for line in self.__lines_to_ignore:
            if line in which_line:
                logging.log(ULTRADEBUG, "Line '%s' contains this "
                              "skippable string: '%s'", which_line, line)
                return True
        return False
    # pylint: disable-msg=R0201,W0613
    def ignore_exception(self, which_exception, on_which_line):
        """Placeholder that you can override to provide more sophisticated
        parsing capabilities. Return True if you want the parser to ignore
        the exception."""
        return False
    def get_line_type(self):
        "Returns the type of the lines that will be created."
        return self.__line_type
    def set_line_type(self, new_line_type):
        "Changes the type of the lines that will be created."
        self.__line_type=new_line_type
    line_type=property(get_line_type, set_line_type)
    def __iter__(self):
        """Iterates over the file, skipping lines that contain ignorable
        snippets and constructing line objects of the specified type for all
        others. Lines that raise exceptions are never reported as they are
        malformed. However, they can be examined by ignore_exception and (if
        ignore_exception returns True) parsing may continue.
        
        We will only allow ParsingErrors to be caught, which should be enough
        to ignore truly known parsing problems.
        """
        for line in Text.__iter__(self):
            if self.is_ignorable(line.lower()):
                continue
            try:
                new_line=self.__line_type(line)
            except ParsingError, which_exception:
                if self.ignore_exception(which_exception, line):
                    pass
                else:
                    logging.error("Unignorable exception on line '%s'", line)
                    raise
            else:
                yield new_line
        return

class ChunkedNLMOutput(NLMOutput):
    """Represents a file associated with a chunkmap. Its iterator returns
    linelists, which are lists of lines logically tied together by the same ID
    in the chunkmap. It assumes (reasonably, I think) that lines belonging to
    the same set are contiguous in the file."""
    def __init__(self, fileobject, type_of_lines, lines_to_ignore, chunkmap, 
                 type_of_line_set=LineList):
        NLMOutput.__init__(self, fileobject, type_of_lines, lines_to_ignore)
        self._chunkmap=chunkmap
        self._lines_type=type_of_line_set
    def __iter__(self):
        current_set=[]
        current_id=None
        bad_id=-1
        for line in NLMOutput.__iter__(self):
            try:
                this_lines_set_id=self._chunkmap.pmid_from_block(line.line_id)
            except KeyError:
                logging.warn("Line without chunkmap equivalent. Emitting"
                                " as id %d", bad_id)
                this_lines_set_id=Pmid(bad_id)
            if this_lines_set_id!=current_id:
                # Is this the first invocation? If not, we have to emit the
                # linelist that just ended, but if it is we'll just pretend
                # that we did.
                if current_id is not None:
                    # Emit the linelist that just ended
                    logging.log(ULTRADEBUG, "Completed set of lines %s "
                                  "according to the chunkmap. Emitting them.",
                                   current_id)
                    if current_id<0:
                        # Decrement bad line counter
                        bad_id-=1
                    yield self._lines_type(current_id, current_set)
                        
                # Start a new, empty linelist
                current_id=this_lines_set_id
                current_set=[]
            current_set.append(line)
        # Is there something left to emit after the iteration's over?
        if len(current_set)>0:
            logging.log(ULTRADEBUG, "Completed iteration. Emitting the last "
                                    "lines left with set id %s", current_id)
            yield self._lines_type(current_id, current_set)
        return
