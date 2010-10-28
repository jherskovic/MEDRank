#!/usr/bin/env python
# encoding: utf-8
"""
setup.py

Created by Jorge Herskovic on 2008-05-29.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""
# TODO: See http://docs.python.org/dist/module-distutils.ccompiler.html to
# try and figure out how to build better.
import sys
import os
from distutils.core import setup, Extension

setup(name="MEDRank",
      version='0.6.1',
      author="Jorge R. Herskovic",
      author_email="jorge.r.herskovic@uth.tmc.edu",
      maintainer="Jorge R. Herskovic",
      maintainer_email="jorge.r.herskovic@uth.tmc.edu",
      license="GPL 2.0",
      description="MEDRank contains information retrieval libraries and "
                  "graph-based ranking classes for biomedical informatics "
                  "research",
      platforms=["any"],
      packages=['MEDRank',
                'MEDRank.computation',
                'MEDRank.evaluation',
                'MEDRank.file',
                'MEDRank.mesh',
                'MEDRank.pubmed',
                'MEDRank.umls',
                'MEDRank.utility'],
      # Warning - this will build a single-threaded version of the library
      ext_modules=[Extension('MEDRank.computation._distmat',
             ['MEDRank/computation/distance/build_distance_matrix.cc'],
             #libraries=["gomp"],
             #library_dirs=['/Developer/usr/lib/gcc/'],
             extra_compile_args=["-ftree-vectorize"],
             include_dirs=["/usr/local/include"],
             language="c++")],
      #package_dir={'MEDRank': 'MEDRank'},
      data_files= [('medrank_data', ["data/mesh09_data.db",
                                "data/mti_converter_data.p",
                                "data/umls_concepts.db",
                                "data/complete_distance_matrix_09.bin",
                                "data/direction_inference.p.bz2"])],
                                
      )
