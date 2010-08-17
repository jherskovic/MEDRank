#!/usr/bin/env python
# encoding: utf-8
"""
text.py

Created by Jorge Herskovic on 2008-04-22.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

class Text(object):
    """Provides standardized handling for text files. The rules are: 
    1. All the text is lowercased. 
    2. Leading and trailing spaces are always stripped. 
    3. No newlines are included (part of the whitespace stripping, but bears
    repeating!) 
    4. Comments are ignored (lines starting with a # as the first
    non-whitespace character)
    5. Empty lines are ignored
    6. Provides an iterator for looping.
    7. The file is consumed after using once - just like a regular file.
    8. Supports rewinding if the underlying file does."""
    def __init__(self, fileobject):
        self.__my_file=fileobject
    def __repr__(self):
        return "<text file based on %r>" % self.__my_file
    def __iter__(self):
        for line in self.__my_file:
            this_line=line.strip()
            if len(this_line)==0:
                continue
            if this_line[0]=='#':
                continue
            yield this_line
        return
    def rewind(self):
        """Restarts reading the file from the beginning."""
        self.__my_file.seek(0)
    def as_list(self):
        """Utility function that returns the contents of a text file as a
        list. Very common usage pattern for data text files."""
        return [x for x in self]
    def as_dict(self, value=None):
        """Utility function that returns the contents of a text file as a
        dictionary, with an optional value for each key. Common usage is: data
        files that will need to be used for membership comparisons."""
        return dict.fromkeys((x for x in self), value)
    def get_file(self):
        """Returns the file object (for a property)"""
        return self.__my_file
    original_file=property(get_file)