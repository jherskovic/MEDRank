#!/usr/bin/env python

"""Takes the UMLS MRCONSO.RRF and builds a cui->one preferred name dictionary.
This dictionary is NOT MEANT TO BE CANONICAL. It is mostly for visualization
and debugging purposes."""

import sys
import random
from MEDRank.utility.output import display_count
import cPickle as pickle

mrconso=open(sys.argv[1], 'rU')

final_dict={}
this_concept=None
these_strings=[]
count=0

for l in mrconso:
    cui, lat, ts, luis, stt, sui, ispref, aui, saui, scui, sdui, sab, \
    ttty, code, _str, srl, suppress, cvf, dummy=l.strip().split('|')

    count+=1
    #display_count(count)

    if cui!=this_concept:
        if this_concept is not None:
            # Concept change, store the decision.
            if len(these_strings)>0:
                final_dict[this_concept]=random.choice(these_strings)
        this_concept=cui
        these_strings=[]
    # Only deal with preferred english concepts
    if lat!='ENG':
        continue
    if ispref=='N':
        continue
    if suppress=='Y':
        continue
    these_strings.append(_str)

# Final pass
if this_concept is not None:
    # Concept change, store the decision.
    final_dict[this_concept]=random.choice(these_strings)
    this_concept=cui
    these_strings=[]

print "The final dictionary has %d concepts." % len(final_dict)
print "Example: C0006142=", final_dict['C0006142']

print "Dumping to", sys.argv[2]
pickle.dump(final_dict, open(sys.argv[2], 'wb'), pickle.HIGHEST_PROTOCOL)