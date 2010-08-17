#!/usr/bin/env python
# encoding: utf-8
"""
build_semantic_predications_cache.py

Created by Jorge Herskovic on 2010-01-12.
Copyright (c) 2010 University of Texas - Houston. All rights reserved.
"""

from MEDRank.file import semantic_predications
from MEDRank.utility import cache
import sys
import os
import bz2
import tempfile
import os.path
import cPickle as pickle
import multiprocessing

def build_dictionary_handler(article_number, links,
                         directory_name=semantic_predications.SEMPRED_CACHE):
    filename=os.path.join(directory_name, "%d.pickle.bz2" % article_number)
    # Use a buffered write
    pickle.dump(links, bz2.BZ2File(filename, 'w', 1000000),
                pickle.HIGHEST_PROTOCOL)

def handle_dictionary_in_another_process(article_number, links, directory_name,             
                                         worker_pool):
    worker_pool.apply_async(build_dictionary_handler,
                            (article_number, links, directory_name))

def dispatcher(task_queue):
    while True:
        t=task_queue.get()
        if t=='STOP':
            break
        workers.apply_async(semantic_predications.parse_xml,
                                (open(t), build_dictionary_handler))
    worker_pool.close()
    worker_pool.join()
    return

def handle_file(filename, handler):
    semantic_predications.parse_xml(open(filename), handler)
    os.unlink(filename)

def main():
    cache.check_for_cache_dir(semantic_predications.SEMPRED_CACHE)
    workers=multiprocessing.Pool()    
    print "Working on cache directory", semantic_predications.SEMPRED_CACHE
    handler=lambda x, y: handle_dictionary_in_another_process(x,
                                y,
                                semantic_predications.SEMPRED_CACHE,
                                workers)
    input_file=open(sys.argv[1])
    # Charge ahead at full speed, use separate processes to do the actual 
    # analysis for each article
    data=tempfile.mktemp()
    #os.close(data[0])
    outfile=open(data, 'w')
    #p=multiprocessing.Process(target=dispatcher, args=(task,))
    #p.start()
    num=0
    for l in input_file:
        #data.append(l)
        #os.write(data[0], l)
        outfile.write(l)
        if '</article>' in l.lower():
            #os.close(data[0])
            outfile.close()
            workers.apply_async(handle_file,
                                    (data, build_dictionary_handler))
            num+=1
            print num, 'articles dispatched. Last file=', data
            data=tempfile.mktemp()
            #os.close(data[0])
            outfile=open(data, 'w')
        #semantic_predications.parse_xml(input_file, handler)
    #task.put('STOP')
    #task.close()
    #task.join_thread()
    #p.join()
    workers.close()
    workers.join()
    print "Done!"

if __name__ == '__main__':
    main()

