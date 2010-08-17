#!/usr/bin/env python
# encoding: utf-8
"""
cache.py

Created by Jorge Herskovic on 2009-09-24.
Copyright (c) 2009 University of Texas - Houston. All rights reserved.
"""

import os
import os.path
# Disable warnings about spaces before operators (they drive me crazy)
# pylint: disable-msg=C0322

USER_HOME=os.path.expanduser("~")
DEFAULT_CACHE_DIR=os.path.join(USER_HOME, ".medrank")

def check_for_cache_dir(cache_dir):
    """Verifies the existence of the cache_dir. If there is no such dir,
    creates it."""
    if not os.access(cache_dir, os.F_OK):
        os.mkdir(cache_dir)
    return

def path():
    """Returns the default path for cached data, creating it if necessary."""
    check_for_cache_dir(DEFAULT_CACHE_DIR)
    return DEFAULT_CACHE_DIR
    
