#!/bin/bash
# Uses the 2007 mrsty table right now, which doesn't matter much because we
# aren't using semantic types for any processing at all

python -O build_concept_data_file.py ../../data/umls_concepts.db \
 ../../data/raw_data/UMLS_2009AA.rtm.bz2 \
 ../../data/raw_data/mrsty.bz2
