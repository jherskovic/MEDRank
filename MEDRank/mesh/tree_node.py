#!/usr/bin/env python
# encoding: utf-8
"""
tree_node.py

Created by Jorge Herskovic on 2008-04-23.
Copyright (c) 2008 University of Texas - Houston. All rights reserved.
"""

from MEDRank.mesh.term import Term

class TreeNode(Term):
    """Represents a node in the MeSH hierarchy."""
    __slots__=Term.__slots__+['__tree_position']
    def __init__(self, term, role, synonyms, tree_position):
        Term.__init__(self, term, role, synonyms)
        # The tree position must always be a set
        if type(tree_position) is not set:
            raise TypeError("The tree position must be a set, but I received"
                            "a %r instead (which is a %r)", tree_position,
                                                    type(tree_position))
        self.__tree_position=tree_position
    def get_pos(self):
        "Getter for the tree position"
        return self.__tree_position
    def set_pos(self, new_pos):
        "Setter for the tree position"
        if type(new_pos) is not set:
            raise TypeError("The tree position must be a set, but I received"
                            " %r instead (which is a %r)", new_pos,
                                                        type(new_pos))
        self.__tree_position=new_pos
    position=property(get_pos, set_pos)
    def get_trees(self):
        """Returns all the trees in which a node is present (useful for
            short-circuiting some evaluations)"""
        return set([x[0] for x in self.position])
    def depths(self):
        """Returns all the known depths in the tree (assuming no unifying root 
        node), in ascending order."""
        my_depths=[x.count('.') for x in self.__tree_position]
        my_depths.sort()
        return my_depths
    def deepest_depth(self):
        """Returns the largest depth at which a node can be found."""
        # Does not use depths() to avoid a sort
        return max(x.count('.') for x in self.__tree_position)
    def shallowest_depth(self):
        """Returns the shallowest depth at which a node can be found."""
        # Does not use depths() to avoid a sort
        return min(x.count('.') for x in self.__tree_position)
    def deepest_position(self):
        """Returns the deepest position in the tree."""
        return max((x.count('.'), x) for x in self.__tree_position)[1]
    def shallowest_position(self):
        """Returns the shallowest position in the tree."""
        return min((x.count('.'), x) for x in self.__tree_position)[1]
    def is_qualifier(self):
        """Determines if a term is a qualifier by using the following
        heuristics:
        Only one position in the tree, the position begins with a Q, and
        has a long string after it, and it isn't a dotted string.
        """
        if len(self.__tree_position)!=1:
            return False
        # Inspect the element - to get a copy, pop it and add it back.
        element=self.__tree_position.pop()
        self.__tree_position.add(element)
        return (element[0].lower()=='q' 
                and len(element)>3 
                and element.count('.')==0)
    def is_descriptor(self):
        """Determines if a term is a descriptor by using the following
        heuristics:
        Only one position in the tree, the position begins with a D, and
        has a long string after it, and it isn't a dotted string.
        """
        if len(self.__tree_position)!=1:
            return False
        # Inspect the element - to get a copy, pop it and add it back.
        element=self.__tree_position.pop()
        self.__tree_position.add(element)
        return (element[0].lower()=='d' 
                and len(element)>3 
                and element.count('.')==0)
    def __getstate__(self):
        tstate=Term.__getstate__(self)
        tstate['pos']=self.__tree_position
        return tstate
    def __setstate__(self, state):
        Term.__setstate__(self, state)
        self.__tree_position=state['pos']
