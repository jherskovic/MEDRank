#!/bin/bash

python -O build_direction_inference_dictionary.py \
 ../../data/direction_inference.p \
 ../../data/raw_data/mrrel.bz2 \
 ../../data/raw_data/mrsty.bz2

echo "Compressing results."
bzip2 -9v ../../data/direction_inference.p