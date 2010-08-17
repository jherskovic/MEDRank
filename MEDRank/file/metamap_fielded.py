#!/usr/bin/env python
# encoding: utf-8
"""
metamap_fielded.py

NOT WORKING RIGHT NOW

Created by Jorge Herskovic on 2008-06-06.
Copyright (c) 2008 University of Texas - Houston. All rights reserved.
"""

import sys
import os
import unittest
from MEDRank.utility.logger import logging, ULTRADEBUG
from MEDRank.file.nlm_output import (Line, ChunkedNLMOutput,
                                     CUINotFoundError, ParsingError,
                                     NoConfidenceError,
                                     NoLineIDError)

class MetamapFieldedLine(Line):
    """Represents a single line of METAMAP Fielded output"""
    __slots__=['_cui', '_description', '_source', '_positions']
    def __init__(self, original_line):
        Line.__init__(self, original_line, id_position=0, split_char='\t')
        line_breakup=self.split_line
        try:
            self._cui=line_breakup[4]
        except IndexError:
            raise CUINotFoundError("There was no CUI in the line '%s'" % 
                                   self._line)
        if self._cui=='':
            raise CUINotFoundError("There was no CUI in the line '%s'" % 
                                   self._line)
        try:
            self._description=line_breakup[3]
            self._source=line_breakup[6]
        except IndexError:
            raise ParsingError("Data missing from line '%s'" % self._line)
        # Some entities have no stated confidence. We use 0 in such cases,
        # so they can be eliminated from the workflow later.
        try:
            self.confidence=float(line_breakup[2])/1000.0
        except ValueError:
            raise NoConfidenceError("Could not parse a confidence value in "
                                    "line '%s'" % self._line)
        logging.log(ULTRADEBUG, "Created a MetamapLine @ %d: %s (%s) %1.3f", 
                      self.line_id, self._cui,
                      self._description, self.confidence)
    # The CUI property.
    def cui_fget(self):
        "Getter for the CUI property"
        return self._cui
    CUI=property(cui_fget)
    # The description property.
    def description_fget(self):
        "Getter for the description property"
        return self._description
    description=property(description_fget)
    # The source property.
    def source_fget(self):
        "Getter for the source property"
        return self._source
    source=property(source_fget)


class MetamapFieldedOutput(ChunkedNLMOutput):
    def __init__(self):
        pass
    def is_ignorable(self, a_line):
        """Check to see if a line should be processed - in the case of 
        METAMAP fielded output, we only want to process actual concept 
        lines. The type of line is determined by the third field of the tab-
        separated list. But first we check to see if the line passes the 
        original tests."""
        # This will preserve the original behavior before adding extra checks
        if ChunkedNLMOutput.is_ignorable(self, a_line):
            return True
        try:
            line_type=a_line.split('\t')[2].lower().strip()
        except IndexError:
            # If it doesn't have a type field, we don't want the line.
            return True
        return line_type!='c' # We only want lines with 'c'
    
        
class metamap_fieldedTests(unittest.TestCase):
    def setUp(self):
        pass


if __name__ == '__main__':
    unittest.main()