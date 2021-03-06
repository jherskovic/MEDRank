#!/usr/bin/env python
# encoding: utf-8
"""
link.py

A set of classes that represent links between two nodes in a graph.

Created by Jorge Herskovic on 2008-05-14.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import operator
# Disable warnings about spaces before and after operators (they drive me crazy)
# pylint: disable-msg=C0322, C0323

class Link(object):
    """Represents a basic directed link between two nodes in a graph.
    The link direction should be encoded in the sign of the link_strength
    parameter.
    
    The Links may also be named in some way.
    """
    __slots__=["_node1", "_node2", "_weight", "_name"]
    def __init__(self, link_node1, link_node2, link_strength, name=None):
        # The link always goes from node1 to node2, so if the strength is
        # negative we'll invert the link.
        
        self._node1, self._node2, self._weight=(link_node1, link_node2,
                                                link_strength) \
                                                if link_strength>=0.0 else \
                                                (link_node2, link_node1,
                                                -link_strength)
        self._name=name
    def __repr__(self):
        weight_repr="--%1.7f-->" % self._weight if self._weight>0.0 else \
                    " -0- "
        name_repr="" if self._name is None else " %s" % self._name
        
        return "<Link%s: %r%s%r>" % (name_repr,
                                     self.node1, 
                                     weight_repr, 
                                     self.node2)
    # The node1 property.
    def node1_fget(self):
        "Getter for the node1 property"
        return self._node1
    def node1_fset(self, value):
        "Setter for the node1 property"
        self._node1=value
    node1=property(node1_fget, node1_fset)
    # The node2 property.
    def node2_fget(self):
        "Getter for the node2 property"
        return self._node2
    def node2_fset(self, value):
        "Setter for the node2 property"
        self._node2=value
    node2=property(node2_fget, node2_fset)
    # The weight property.
    def weight_fget(self):
        "Getter for the weight property"
        return self._weight
    def weight_fset(self, value):
        "Setter for the weight property"
        # If the weight is negative, that means that the link points in the
        # other direction. Hence, we must flip it!
        if value<0.0:
            value=-value
            self._node1, self._node2=self._node2, self._node1
        self._weight=value
    weight=property(weight_fget, weight_fset)
    # The name property.
    def name_fget(self):
        "Getter for the name property"
        return self._name
    def name_fset(self, value):
        "Setter for the name property"
        self._name=value
    name=property(name_fget, name_fset)
    def __eq__(self, other):
        """Two links are the same if they point to the same nodes, in any
        same direction."""
        # Direct access to properties saves a lot of execution time
        return (self._node1==other._node1 and self._node2==other._node2)
    def __hash__(self):
        """We respect the order of the nodes here (not in AdirectionalLink)."""
        n1=hash(self._node1)
        n2=hash(self._node2)
        return (n1 << 2) ^ n2
    def __getstate__(self):
        return {'x': self._node1,
                'y': self._node2,
                'w': self._weight,
                'n': self._name}
    def __setstate__(self, state):
        self._node1=state['x']
        self._node2=state['y']
        self._weight=state['w']
        self._name=state['n']
        
class AdirectionalLink(Link):
    """A link between two nodes in a graph, but without a direction.
    Since the link is not directional, the link_strength's absolute value is
    used."""
    # This class doesn't need its own slots
    __slots__=[]
    def __init__(self, link_node1, link_node2, link_strength, name=None):
        Link.__init__(self, link_node1, link_node2, abs(link_strength), name)
    # The weight property.
    def weight_fset(self, value):
        "New setter for the weight property"
        Link.weight_fset(self, abs(value))
    weight=property(Link.weight_fget, weight_fset)
    def __repr__(self):
        weight_repr="==%1.7f==" % self._weight if self._weight>0.0 else \
                    " -0- "
        name_repr="" if self.name is None else " %s" % self.name
        
        return "<Link%s: %r%s%r>" % (name_repr,
                                     self.node1, 
                                     weight_repr, 
                                     self.node2)
    def __hash__(self):
        """Since the links are the same if the nodes pointed to are the same,
        regardless of order, we have to use a commutative operation to
        integrate the hashes."""
        n1=hash(self.node1)
        n2=hash(self.node2)
        return n1 ^ n2
    def __eq__(self, other):
        """Two links are the same if they point to the same nodes, in any
        same direction."""
        return (self.node1==other.node1 and self.node2==other.node2) or \
               (self.node1==other.node2 and self.node2==other.node1)
