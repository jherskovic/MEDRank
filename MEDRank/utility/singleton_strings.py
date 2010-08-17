#!/usr/bin/env python
# encoding: utf-8
"""
singleton_strings.py

Created by Jorge Herskovic on 2008-04-22.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.

This file may be overkill; I think I won't use it at the beginning, and will only end up calling on it if memory usage becomes ludicrous.
"""

class SingletonString(object):
    """Replaces strings with object references to save memory. The singleton
    strings behave like strings but are slower to access and manipulate. Since
    storing a singleton string requires a dictionary mapping, a list entry,
    and two references to the object it will only be done if the candidate
    string is long enough.
    
    Singleton strings are intended to handle the large amounts of repetition
   when working with certain UMLS files."""
    string_store={}
    reverse_mapping=[]
    mapping_threshold=12 # Anything below this doesn't get mapped
    slots=['__n']
    def __init__(self, my_string):
        if len(my_string)<SingletonString.mapping_threshold:
            self.__n=my_string
            return
        # This pattern expects lots of repetition
        try:
            self.__n=SingletonString.string_store[my_string]
        except KeyError:
            SingletonString.reverse_mapping.append(my_string)
            self.__n=len(SingletonString.reverse_mapping)-1
            SingletonString.string_store[my_string]=self.__n
    def __str__(self):
        if type(self.__n) is str:
            return self.__n
        return SingletonString.reverse_mapping[self.__n]
    def __repr__(self):
        return self.__str__()
    def __eq__(self, other):
        if isinstance(other, SingletonString):
            return self.__n==other.__n
        else:
            return self.__str__()==other.__str__()
    def __ge__(self, other):
        # This will work for regular AND singleton strings
        return self.__str__()>=other.__str__()
    def __le__(self, other):
        return self.__str__()<=other.__str__()
    def __ne__(self, other):
        return not self.__eq__(other)
    def __lt__(self, other):
        return self.__str__()<other.__str__()
    def __gt__(self, other):
        return self.__str__()>other.__str__()
    def __add__(self, other):
        """Returns a NORMAL string. If you want to save it as a
        singleton_string, you'll have to construct a new one. This function is
        expected to be used very little, if at all. """
        return self.__str__()+other.__str__()
    def __mul__(self, other):
        """Returns a NORMAL string. If you want to save it as a
        singleton_string, you'll have to construct a new one. This function is
        expected to be used very little, if at all. """
        return self.__str__() * other
    def secret_identity(self):
        """Debugging function, returns the internal representation of the
        string."""
        return self.__n

