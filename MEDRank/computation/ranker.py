#!/usr/bin/env python
# encoding: utf-8
"""
ranker.py

Describes a generic, base ranker from which other rankers can inherit.

Created by Jorge Herskovic on 2008-06-18.
Copyright (c) 2008 University of Texas - Houston. All rights reserved.
"""

from MEDRank.utility.logger import logging, ULTRADEBUG

class RankerStats(object):
    """Auxilliary class that holds the statistics for a ranking run."""
    def __init__(self, iterations, accumulator, start_time, start_iter_time,
                 end_time):
        self._iterations=iterations
        self._accumulator=accumulator
        self._start_time=start_time
        self._start_iter_time=start_iter_time
        self._end_time=end_time
    def __repr__(self):
        try:
            runtime=self._end_time-self._start_time
            speed="%s" % (float(self._iterations)/(runtime))
        except ZeroDivisionError:
            speed="Too short to measure"
        return "<RankerStats: %d iterations in %s seconds (%s were setup)" \
               "=%s iterations/second (final accumulator=%s)>" % (
               self._iterations, runtime, 
               self._start_iter_time-self._start_time,
               speed,
               self._accumulator)

class Ranker(object):
    def __init__(self, damping_factor=0.85, max_iterations=10000, 
                 epsilon=0.0001):
        logging.log(ULTRADEBUG, "Creating a ranker object.")
        self._max_iter=max_iterations
        self._e=epsilon
        self._d=damping_factor
        self._latest_stats=None
    def __repr__(self):
        return "<%s: epsilon %1.7f damping factor %1.7f " \
               "max_iter %d>" % (self.__class__.__name__,
                                 self._e, self._d, self._max_iter)
    def get_stats(self):
        """Returns information about the last PageRank computation performed
        by this ranker."""
        return self._latest_stats
    stats=property(get_stats)
    def get_max_iterations(self):
        return self._max_iter
    def set_max_iterations(self, number_iterations):
        if number_iterations < 0:
            raise ValueError("The number of iterations for a ranker should be positive.")
        self._max_iter=number_iterations
    max_iterations=property(get_max_iterations, set_max_iterations)