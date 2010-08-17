#!/usr/bin/env python
# encoding: utf-8
"""
build_pubmed_cache.py

Takes a file produced by the Medline Baseline Repository project 
(at http://mbr.nlm.nih.gov) and repurposes it into a cache of the entire corresponding 
MEDLINE copy. We use the Full_MH_SH_items files, and those are the only ones this tool
will read.

For example,
http://mbr.nlm.nih.gov/Download/2008/Data/Full_MH_SH_items.gz

Fair warning: Speedy, memory-efficient. Choose one. I chose memory-efficient because
I'm too lazy to install 64-bit python on my Mac. I did multiprocess-enable it because the
dataset is huge and the processing is SLOW otherwise.

The format this produces should be a reasonable clone of the Bio.MEDLINE module records

Created by Jorge Herskovic on 2009-10-09.
Copyright (c) 2009 UTHSC School of Health Information Sciences. All rights reserved.
"""

import sys
import os
from MEDRank.file.disk_backed_dict import StringDBDict, SYNC_KEY, COUNTER_KEY, WRITE_EVERY_KEY
import gzip
import cPickle as pickle                                
import multiprocessing
import sqlite3
import traceback

def get_term_from_line(a_line):
    """Takes a line from the input (in the Full_MH_SH format, see 
    http://mbr.nlm.nih.gov/Download/2008/Data/README) and returns a PMID, term pair
    in a format similar to MEDLINE.Record"""
    decomposed=a_line.split('|')
    major=decomposed[0]
    subheading=decomposed[1]
    if int(decomposed[2])==1:
        starred='*'
    else:
        starred=''
    if len(subheading)>0:
        subheading='%s%s' % (starred, subheading)
    else:
        major='%s%s' % (starred, major)
    pmid=decomposed[3]
    return (pmid, major, subheading)
    
def pickle_records(in_queue, out_queue):
    while True:
        in_rec=in_queue.get()
        #print in_rec
        if in_rec=='STOP':
            #in_queue.task_done()
            break
        try:
            pmid, data=in_rec
            pickled=pickle.dumps(data, pickle.HIGHEST_PROTOCOL)
            out_queue.put((pmid, pickled))
        except:
            print "ERROR:", traceback.format_exc()
        #finally:
        #    in_queue.task_done()
    out_queue.put('STOP')
    out_queue.close()
    return
    
def write_records(in_queue, database_filename):
    """Simulates the creation of a normal DBDict (for speed reasons)"""
    my_db=sqlite3.connect(database_filename)
    my_db.text_factory=str
    my_db.execute("create table s (pkey TEXT NOT NULL, data BLOB NOT NULL)") # No index - we'll add it later
    print "Database and table created"
    while True:
        in_rec=in_queue.get()
        if in_rec=='STOP':
            #in_queue.task_done()
            break
        try:
            pmid, data=in_rec
            my_db.execute('INSERT INTO S VALUES (?, ?)', [pmid, data])
        except:
            print "ERROR:", traceback.format_exc()
        #finally:
        #    in_queue.task_done()
    # Create the missing index
    print "Creating the missing index"
    my_db.execute('CREATE UNIQUE INDEX ix_s ON s (pkey)')
    print "Done creating index. Creating the rest of the DBDict structure."
    my_db.execute('INSERT INTO S VALUES (?, ?)', [SYNC_KEY, pickle.dumps(1)])
    my_db.execute('INSERT INTO S VALUES (?, ?)', [WRITE_EVERY_KEY, pickle.dumps(1)])
    my_db.execute('INSERT INTO S VALUES (?, ?)', [COUNTER_KEY, pickle.dumps(0)])
    print "Commiting everything."
    my_db.commit()
    my_db.close()
    return
    
def decompress_original(original_file, resulting_queue):
    input_file=gzip.GzipFile(original_file)
    for line in input_file:
        resulting_queue.put(line)
    resulting_queue.put(None)
    return
    
def main():
    #input_file=gzip.GzipFile(sys.argv[1])
    # Commits disabled at the beginning for speed
    #output_dict=StringDBDict(sys.argv[2], sync_every_transactions=0, 
    #                         write_out_every_transactions=100000,
    #                         compression=False)
    to_pickle=multiprocessing.Queue(1000)
    to_database=multiprocessing.Queue(1000)
    from_file=multiprocessing.Queue(10000)
    pickler=multiprocessing.Process(target=pickle_records, args=(to_pickle, to_database), name="Pickler")
    writer=multiprocessing.Process(target=write_records, args=(to_database, sys.argv[2]), name="Writer")
    reader=multiprocessing.Process(target=decompress_original, args=(sys.argv[1], from_file), name="Reader")
    reader.start()
    pickler.start()
    writer.start()
    lines=0
    cache={}
    #terms_dict={}
    #term_num=0
    lastarticle=None
    articles=0
    repeated_keys=0
    #for line in input_file:
    while True:
        line=from_file.get()
        if line is None: 
            break
        pmid, mh, sh=get_term_from_line(line)
        #pmid=int(pmid)
        if pmid!=lastarticle and lastarticle is not None:
            #if len(cache)>=100000:
            #    for k,v in cache.iteritems():
            #        outlist=[]
            #        for x in v:
            #            newlist=[x] + v[x]
            #            outlist.append('/'.join(newlist))
            #        outlist.sort()
            #        #output_dict[k]={'MH': outlist}
            #        output_dict.write('%d|%s\n' % (k, '|'.join(outlist)))
            #        articles+=1
            #        if articles % 1000 == 0:
            #            print "Output %d articles so far" % articles
            #    cache={}
            outlist=[]
            k=cache.keys()[0] # There should only be one key anyway
            v=cache[k]
            for x in v:
                newlist=[x] + v[x]
                outlist.append('/'.join(newlist))
            outlist.sort()
            output_dict={'MH': outlist}
            to_pickle.put((k, output_dict))
            articles+=1
            #if articles % 1000 == 0:
            #    print "Output %d articles so far" % articles
            cache={}
        #try:
        #    if sh=='':
        #        sh=-1
        #    else:
        #        sh=terms_dict[sh]
        #except KeyError:
        #    terms_dict[sh]=term_num
        #    sh=term_num
        #    term_num+=1
        #try:
        #    mh=terms_dict[mh]
        #except KeyError:
        #    terms_dict[mh]=term_num
        #    mh=term_num
        #    term_num+=1
        #    
        try:
            curr_rec=cache[pmid]
        except KeyError:
            curr_rec={}
        if mh in curr_rec:
            curr_rec[mh].append(sh)
        else:
            #if sh>=0:
            if len(sh)>0:
                curr_rec[mh]=[sh]
            else:
                curr_rec[mh]=[]
        cache[pmid]=curr_rec
        lines+=1
        if lines % 1000 == 0:
            print "Processed %d lines so far." \
                % (lines)
            
        lastarticle=pmid
    to_pickle.put("STOP")
    to_pickle.close()
    print "Done reading original file. Waiting for the pickler to catch up."
    to_pickle.join_thread()
    print "Done pickling. Waiting for database output to end."
    pickler.join()
    
    to_database.join_thread()
    print "Done storing in the database. Waiting for database cleanup to end."
    writer.join()
    
    print "Done."
    return

if __name__ == '__main__':
    main()

