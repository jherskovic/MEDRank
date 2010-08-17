#!/usr/bin/env python
# encoding: utf-8
"""
proctitle.py

Uses the setproctitle python module, if available,
to set a process's title. Otherwise it's just a NOP.

Created by Jorge Herskovic on 2010-05-25.
Copyright (c) 2010 Jorge Herskovic. All rights reserved.
"""

try:
    from setproctitle import setproctitle
except ImportError:
    def setproctitle(x): pass
