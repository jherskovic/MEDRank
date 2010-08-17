#!/usr/bin/env python
# encoding: utf-8
"""
logger.py

MEDRank's logging facility. Required to enable multiprocessing logging.

Created by Jorge Herskovic on 2009-04-01.
Copyright (c) 2009 University of Texas - Houston. All rights reserved.
"""

try:
    import multiprocessing
    multiprocessing_available=True
except ImportError:
    multiprocessing_available=False
    
# pylint: disable-msg=W0611
from logging import (INFO, DEBUG, WARNING, StreamHandler, Formatter)
if not multiprocessing_available:
    from logging import getLogger

# Disable warnings about spaces before operators (they drive me crazy)
# pylint: disable-msg=C0322

ULTRADEBUG=DEBUG/2 # INSANE DETAIL LEVEL

CH=StreamHandler()
FORMATTER=Formatter('%(processName)s %(asctime)s %(levelname)s %(module)s.' \
                      '%(funcName)s: %(message)s')
CH.setFormatter(FORMATTER)

# pylint: disable-msg=C0103
if multiprocessing_available:
    logging=multiprocessing.get_logger()
else:
    logging=getLogger()
    
logging.addHandler(CH)
logging.setLevel(INFO)

