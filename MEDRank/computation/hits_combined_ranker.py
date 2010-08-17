#!/usr/bin/env python
# encoding: utf-8
"""
hits_combined_ranker.py

Allows the user to specify how to combine the Authorities and Hubs scores from
the original HITS ranker to compute a single score. The specification is done
by passing a function that takes two parameters and outputs a single value.

By default it outputs the authority score.

Created by Jorge Herskovic on 2008-06-18.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""
from base_hits_ranker import HITSRanker
# Disable warnings about spaces before and after operators (they drive me crazy)
# pylint: disable-msg=C0322, C0323

# Don't warn about the unused hub score. We need it to prototype the function
# correctly.
# pylint: disable-msg=W0613
def default_combination_function(authority_score, hub_score):
    """This is a dummy function used as a placeholder. By default it computes
    just the authority score. If you want to compute some combination of the
    authority and hub scores, pass a function that does so to the 
    HITSCombinedRanker constructor."""
    return authority_score

class HITSCombinedRanker(HITSRanker):
    """Allows the user to specify how to combine the Authorities and Hubs
    scores from the original HITS ranker to compute a single score. The
    specification is done by passing a function that takes two parameters and
    outputs a single value.

    By default it outputs the authority score."""
    def __init__(self, damping_factor=0.85, max_iterations=10000, 
                 epsilon=0.0001,
                 combination_function=default_combination_function):
        HITSRanker.__init__(self, damping_factor, max_iterations, epsilon)
        self._combination_function=combination_function
    def evaluate(self, link_matrix):
        """Performs the actual ranking."""
        (auth_scores, hub_scores)=HITSRanker.evaluate(self, link_matrix)
        final_scores=[self._combination_function(x[0], x[1]) for x in
                      zip(auth_scores, hub_scores)]
        return final_scores
