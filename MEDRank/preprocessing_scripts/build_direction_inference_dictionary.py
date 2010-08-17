#!/usr/bin/env python
# encoding: utf-8
"""
build_direction_inference_dictionary.py

Created by Jorge Herskovic on 2008-06-24.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import sys
from MEDRank.file.mrrel import MRRELTable
from MEDRank.file.mrsty import MRSTYTable
from bz2 import BZ2File
from MEDRank.umls.infer_relation_direction import *
from MEDRank.umls.semantic_types import *
import cPickle as pickle

my_format_string='%(asctime)s %(levelname)s %(module)s.' \
                   '%(funcName)s: %(message)s'
logging.basicConfig(level=logging.DEBUG, format=my_format_string)

infile=MRRELTable(BZ2File(sys.argv[2]))
styfile=MRSTYTable(BZ2File(sys.argv[3]))
print "Loading semantic type table."
stytable=SemanticTypes()
stytable.build_from_mrsty_file(styfile)
print "Loading relationship table."
inferrer=RelationDirectionInferrer()
inferrer.build_from_mrrel_file_and_stype_table(infile, stytable)
print "Done. Saving results."
pickle.dump(inferrer, open(sys.argv[1], 'wb'), pickle.HIGHEST_PROTOCOL)
