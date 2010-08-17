#!/usr/bin/env python
# encoding: utf-8
"""
bidirectional_search.py

Performs a bidirectional search on a LinkMatrix to obtain the shortest distance
between two concepts. Returns a list containing the route.

Modified from the implementation available at 
http://popcnt.org/2008/03/bidirectional-search-example.html
to support directional links, and run on an link matrix.

Created by Jorge Herskovic on 2008-06-19.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""
# Disable warnings about spaces before operators (they drive me crazy)
# pylint: disable-msg=C0322

# Don't bug me about single-letter variable names. This is a classic algorithm.
# pylint: disable-msg=C0103
def search(matrix, transposed, point_a, point_b):
    """Performs a bidirectional search on a LinkMatrix to obtain the shortest 
       distance between two concepts. Returns a list containing the route. 
       You must pre-transpose the matrix to give this a chance of completing
       some day."""
    def build_next_level(paths, previous_level, successor_generator):
        """Constructs the next search level."""
        new_level=[]
        for each_node in previous_level:
            for candidate_node in successor_generator(each_node):
                if candidate_node not in paths:
                    paths[candidate_node]=each_node
                    new_level.append(candidate_node)
        return new_level
    
    # Setup computation
    paths_a={ point_a: None }
    paths_b={ point_b: None }
    
    last_a=[point_a]
    last_b=[point_b]
    
    while len(last_a) and len(last_b):
        # print "Paths a=", paths_a, "paths b=", paths_b
        a_nodes=set(paths_a.keys())
        b_nodes=set(paths_b.keys())
        middle_nodes=a_nodes.intersection(b_nodes)
        if middle_nodes:
            break # solution found!
        if len(a_nodes)<=len(b_nodes):
            last_a=build_next_level(paths_a, last_a, matrix.neighbors)
        else:
            last_b=build_next_level(paths_b, last_b, transposed.neighbors)
    else:
        return [] # Empty solution
        
    # Generate the final path, from a->middle->b
    middle=list(middle_nodes)[0]
    res=[]
    c=middle
    # middle to a
    while c!=point_a:
        c=paths_a[c]
        res.insert(0, c)
    res.append(middle)
    # middle to b
    c=middle
    while c!=point_b:
        c=paths_b[c]
        res.append(c)
        
    return res
    