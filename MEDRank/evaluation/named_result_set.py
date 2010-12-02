#!/usr/bin/env python
# encoding: utf-8
"""
named_result_set.py

NamedResultSet is a class that injects its own given name before every column
name, therefore enabling more results to exist for a single experiment.

Created by Jorge Herskovic on 2009-03-26.
Copyright (c) 2009 University of Texas - Houston. All rights reserved.
"""

from result_set import ResultSet
from result import Result

class NamedResult(Result):
    def __init__(self, prefix, OriginalResult):
        Result.__init__(self, OriginalResult.result)
        self.__original_class_name=OriginalResult.column_name()
        self.__prefix=prefix
    def column_name(self):
        return self.__prefix+self.__original_class_name
    
class NamedResultSet(ResultSet):
    """A ResultSet that returns differently-named results."""
    def prefix():
        doc = "The prefix property."
        def fget(self):
            return self._prefix
        def fset(self, value):
            self._prefix = value
        def fdel(self):
            del self._prefix
        return locals()
    prefix = property(**prefix())
    def __init__(self, prefix, another_result_set):
        ResultSet.__init__(self)
        self._prefix=prefix
        for i in another_result_set:
            self.add(NamedResult(prefix, i))
#    def __iter__(self):
#        for k in ResultSet.__iter__(self):
#            yield NamedResult(self.prefix, k)
#        return
#    def pop(self):
#        tempresult=ResultSet.pop(self)
#        return NamedResult(self.prefix, tempresult)
    