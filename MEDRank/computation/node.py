#!/usr/bin/env python
# encoding: utf-8
"""
node.py

Represents a node in a link-node graph.

Created by Jorge Herskovic on 2008-05-14.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

class Node(object):
    """Represents a node in a graph. Can also optionally keep a record of the original
    line from the file (useful for certain MTI applications)."""
    __slots__=['_name', '_node_id', '_weight', '_original']
    def __init__(self, node_id, node_name, node_weight, original_line=None):
        self._name=node_name
        self._node_id=node_id
        self._weight=node_weight
        self._original=original_line
    def __repr__(self):
        return "<node object %s (%s) %1.7f>" % (self._node_id, self._name, 
                                                self._weight)
    # The name property.
    def name_fget(self):
        "Getter for the name property"
        return self._name
    def name_fset(self, value):
        "Setter for the name property"
        self._name=value
    name=property(name_fget, name_fset)
    # The node_id property.
    def node_id_fget(self):
        "Getter for the node_id property"
        return self._node_id
    def node_id_fset(self, value):
        "Setter for the node_id property"
        self._node_id=value
    node_id=property(node_id_fget, node_id_fset)
    # The weight property.
    def weight_fget(self):
        "Getter for the weight property"
        return self._weight
    def weight_fset(self, value):
        "Setter for the weight property"
        self._weight=value
    weight=property(weight_fget, weight_fset)
    def original_fget(self):
        return self._original
    def original_fset(self, value):
        self._original = value
    original=property(original_fget, original_fset)
    def __eq__(self, other):
        # Direct access to the property makes for a much faster call
        return self._node_id==other._node_id
    def __hash__(self):
        return hash(self.node_id)
    # Pickle support for classes with slots requires get and setstate methods
    def __getstate__(self):
        return {'n': self._name,
                'i': self._node_id,
                'w': self._weight,
                'o': self._original}
    def __setstate__(self, state):
        self._name=state['n']
        self._node_id=state['i']
        self._weight=state['w']
        self._original=state['o']
    