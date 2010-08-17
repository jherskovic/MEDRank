#!/usr/bin/env python
# encoding: utf-8
"""
build_checktag_boost_lists.py

Takes the CSV files in a Zip file (originally from MEDRank V1)

Created by Jorge Herskovic on 2008-05-19.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

import tempfile
from MEDRank.utility.logger import logging
from zipfile import ZipFile
from StringIO import StringIO
from csv import (DictReader, Sniffer )
import os
from MEDRank.umls.converter import ConverterData
import cPickle
import sys

def read_lists(the_zip):
    lists={}
    zf=ZipFile(the_zip)
    files=zf.namelist()
    for each_file in files:
        try:
            listname=os.path.splitext(os.path.basename(each_file))[0].lower()
            logging.debug('Reading UMLS Checktag boost list %s from file %s',
                          listname,
                          each_file)
            this_list={}
            row_counter=0
            # To handle boneheadedness on behalf of the CSV readers, we'll
            # use a temporary file
            filedata=zf.read(each_file)
            tmphandle, tmpname=tempfile.mkstemp()
            os.write(tmphandle, filedata)
            os.fsync(tmphandle)
            os.close(tmphandle)
            print "Decompressed %s into %s. Processing it." % (each_file, 
                                                               tmpname)
            fakefile=open(tmpname, 'rU')
            this_reader=DictReader(fakefile)
            for item in this_reader:
                row_counter+=1
                if item['Row'].strip()=='':
                    raise ValueError('Blank line in UMLS file %s when '
                                     'expecting row %d', each_file, row_counter)
                if int(item['Row']) != row_counter:
                    raise ValueError("Inconsistent UMLS list file %s",
                                     each_file)
                this_list[item['CUI'].strip().lower()]=\
                    item['Description'].strip().lower()
            os.unlink(tmpname)
            lists[listname]=this_list
        except:
            logging.debug("Exception happened while processing file %s",
                          each_file)
            raise
    return lists

def main():
    original_zipfile=sys.argv[3]
    original_codefile=sys.argv[2]
    lists=read_lists(original_zipfile)
    execfile(original_codefile)
    cPickle.dump(ConverterData(lists, locals()['checktag_rules'],
                                      locals()['subheading_rules'],
                                      locals()['extra_from_trees'],
                                      locals()['known_bad_terms']),
                                      open(sys.argv[1], 'wb'),
                 cPickle.HIGHEST_PROTOCOL)

if __name__ == '__main__':
    main()