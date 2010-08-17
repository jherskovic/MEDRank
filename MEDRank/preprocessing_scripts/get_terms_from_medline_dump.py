#!/usr/bin/env python
# encoding: utf-8
"""
get_terms_from_medline_dump.py

Created by Jorge Herskovic on 2009-04-03.
Copyright (c) 2009 University of Texas - Houston. All rights reserved.
"""

import sys
import gzip
import os
from xml.parsers.expat import ParserCreate
#from MEDRank.file.disk_backed_dict import StringDBDict
import sqlite3
from glob import glob
import cPickle
from multiprocessing import Pool

currently_in_article=False
current_article=None
current_tag=None
current_terms=[]
current_heading=''
term_is_major=False
my_article_terms={}

def start_element(name, attrs):
    global currently_in_article, current_terms, current_tag, term_is_major
    if name=='MedlineCitation':
        currently_in_article=True
    if currently_in_article:
        if name=='PMID':
            current_tag='PMID'
        if name in ['DescriptorName', 'QualifierName']:
           current_tag=name
           term_is_major=attrs['MajorTopicYN']=='Y'
            
def character_data(data):
    global current_tag, current_article, current_heading
    data=data.encode('ascii', 'ignore')
    if current_tag=='PMID':
        current_article=data
    if current_tag in ['DescriptorName', 'QualifierName']:
        if len(current_heading)>0:
            current_heading+='/'
        if term_is_major:
            current_heading+='*'
        current_heading += data
    
def end_element(name):
    global currently_in_article, current_article, current_tag, current_terms
    global current_heading, my_article_terms
    if name=='MedlineCitation':
        # print "Article %s terms=%r" % (current_article, current_terms)
	if current_article is not None:
            my_article_terms[current_article]=current_terms
        currently_in_article=False
        current_article=None
        current_tag=None
        current_terms=[]
    if name==current_tag:
        current_tag=None
    if name=='MeshHeading':
        current_terms.append(current_heading.lower())
        current_heading=''

def process_one_file(filename):
    global my_article_terms
    print "Processing", filename
    p=ParserCreate()
    p.StartElementHandler=start_element
    p.EndElementHandler=end_element
    p.CharacterDataHandler=character_data
    my_article_terms={}
    p.ParseFile(gzip.GzipFile(filename))
    return my_article_terms
    
def main():
    global article_terms
    article_terms=sqlite3.connect(sys.argv[1])
    article_terms.execute("""CREATE TABLE s (pkey TEXT PRIMARY KEY NOT NULL ,
                                             data BLOB NOT NULL)""")
    article_terms.text_factory=str
    curs=article_terms.cursor()
    pool=Pool()
    results=[pool.apply_async(process_one_file, (x,)) 
                for x in glob("*.xml.gz")]
    count=0
    while True:
        try:
            a_result=results.pop(0)
        except IndexError:
            break
        this_result=a_result.get()
        curs.executemany("INSERT OR REPLACE INTO s VALUES (?, ?)", 
                            ((x[0], 
                              buffer(cPickle.dumps(x[1],
                                                   cPickle.HIGHEST_PROTOCOL))) 
                             for x in this_result.iteritems()))
        article_terms.commit()
        #for k, v in this_result.iteritems():
        #    article_terms[k]=v
        count += 1
        print "Results from %d files processed so far." % count
    article_terms.close()
    
if __name__ == '__main__':
    main()

