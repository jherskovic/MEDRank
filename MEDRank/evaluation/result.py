#!/usr/bin/env python
# encoding: utf-8
"""
result.py

Represents a single evaluation result. The idea is to mix the data from the
evaluation with metadata about it, so that the results are self-describing.
Each evaluation will (under this regime) produce a single result. 

In general, evaluations map to the real numbers. This could be abused via
python's duck-typing, and I'm not clear if that would be a good idea or not. 
I won't mess with it for now.

Created by Jorge Herskovic on 2008-05-15.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

class Result(object):
    """Represents the result of a single evaluation. This class is meant to be
    subclassed by each evaluation, which must provide its own Result with
    metadata about the test. Once set, the value of Result is immutable."""
    __slots__=["__result"]
    def __init__(self, result_value):
        self.__result=result_value
    # The result property.
    def result_fget(self):
        "Getter for the result property"
        return self.__result
    result=property(result_fget)
    def __eq__(self, other):
        return type(self) is type(other) and self.__result==other.result
    def __hash__(self):
        # The hash must be equal for objects that compare equal. In this case,
        # the string representations will have to be the same. For the typical
        # use case of float or int return values, this will work just fine.
        return hash(self.__repr__())
    def __ne__(self, other):
        return not self.__eq__(other)
    def __repr__(self):
        return "<%s: %r>" % (self.column_name(), self.__result)
    def column_name(self):
        """The name of a potential database column"""
        return self.__class__.__name__
