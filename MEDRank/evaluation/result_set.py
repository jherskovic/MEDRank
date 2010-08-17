#!/usr/bin/env python
# encoding: utf-8
"""
result_set.py

Represents a set of evaluation results. Evaluators are not called directly by 
code; they are called by GroupedEvaluators, that bunch together a set of 
evaluations and return result_sets.

Created by Jorge Herskovic on 2008-05-15.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

class ResultSet(set):
    """A ResultSet is a set of evaluation results."""
    def columns(self):
        my_columns=[]
        for x in self:
            my_columns.append(x.column_name())
        return set(my_columns)
    def __repr__(self):
        return "<%s containing: %r>" % (self.__class__.__name__,
                                        list([x for x in self]))
    def as_dict(self):
        """Outputs the result set as a name->value dictionary (mostly 
        useful for output)"""
        result={}
        for x in self:
            result[x.column_name()]=x.result
        return result
