#!/usr/bin/env python
# encoding: utf-8
"""
multithreaded_workflow.py

Created by Jorge Herskovic on 2010-07-01.
Copyright (c) 2010 University of Texas - Houston. All rights reserved.
"""

from MEDRank.utility.logger import logging, ULTRADEBUG
import os
import traceback
import operator
import sys
import gc
from csv import DictWriter
import cPickle as pickle
import cStringIO as StringIO
#from multiprocessing import (Queue, JoinableQueue, cpu_count, Process, 
#                             current_process, get_logger, Pipe)
from threading import Thread
from Queue import Queue
from MEDRank.file.disk_backed_dict import StringDBDict
from MEDRank.umls.concept import Concept
from MEDRank.pubmed.pmid import Pmid
from MEDRank.utility.output import *
from MEDRank.utility.process import processor

def multi_processor(reader,
                    workflow_class,
                    graph_builder_constructor, graph_builder_params,
                    ranker_constructor, ranker_params,
                    eval_parameters, 
                    ranking_cutoff,
                    mesh_tree_filename, distance_matrix_filename,
                    distance_function,
                    umls_converter_data_filename,
                    umls_concept_data_filename,
                    extra_data_name,
                    extra_data_contents,
                    output_file,
                    num_threads=None,
                    queue_size=None,
                    output_callback=output,
                    output_headers_callback=output_headers,
                    output_item_callback=output_one_item,
                    performance_tuning=True):
    """
    Perform the evaluation.
    Multithreading notes: It's the responsibility of the caller to make sure
    that extra_data_contents, if any, are thread-safe. 
    """
    if num_threads is None:
        num_threads=1

    logging.debug("Initializing Concept storage from %s", 
                  umls_concept_data_filename)
                  
    # Since there's no direct way of setting the concept cache's title, 
    # we set it here, wait for it to be inherited, and then get the 'real' 
    # process title for this one. 
    if umls_concept_data_filename is None:
        Concept.init_storage()
    else:
        Concept.init_storage(StringDBDict(umls_concept_data_filename))
    Pmid.init_storage()

    threads=[]
    logging.info("Creating %d worker threads.", num_threads)
    #task_queue=[JoinableQueue(queue_size) for x in xrange(num_processes)]
    task_queues=[Queue(queue_size) for x in xrange(num_threads)]
    this_output_queue=Queue(2*queue_size)

    # Create an output processor
    output_processor=Thread(target=output_callback, 
                             args=(output_file, 
                                   this_output_queue,
                                   output_headers_callback,
                                   output_item_callback))
    output_processor.start()
    
    for i in xrange(num_threads):
        this_thread=Thread(target=processor, args=(workflow_class,
                                                graph_builder_constructor, 
                                                graph_builder_params,
                                                ranker_constructor, 
                                                ranker_params,
                                                eval_parameters, 
                                                ranking_cutoff,
                                                mesh_tree_filename,
                                                distance_matrix_filename,
                                                distance_function,
                                                umls_converter_data_filename,
                                                extra_data_name,
                                                extra_data_contents,
                                                task_queues[i],
                                                this_output_queue),
                             name="MEDRank-Worker-%d" % i)
        logging.log(ULTRADEBUG, "Created thread: %r", this_thread)
        this_thread.start()
        threads.append((this_thread, this_output_queue, task_queues[i]))
    
    all_results={}
    count=0

    # Use a single dispatch queue for automagical load balancing
    # CHANGED - Now uses multiple queues to avoid starving due to waiting on semlocks
    for each_article in reader:
        count+=1
        # logging.info("Dispatching article %d: %r", count, each_article)
        target_thread=(count-1) % num_threads
        logging.info("Dispatching article %d: %s to %s", 
                     count,
                     each_article.set_id,
                     threads[target_thread][0].name)
        task_queues[target_thread].put(each_article)
        #task_queue[target_process].put(each_article)
        #task_queue.put(each_article)
        #logging.info("The task queue is approximately %d items long.", 
        #             task_queue.qsize())

    logging.log(ULTRADEBUG, "Waiting for processing to end.")
    all_results={}

    alive_threads=[x for x in threads if x[0].is_alive()]
    remaining_threads=len(alive_threads)

    logging.info("There are %d threads (out of %d) still alive.", 
                 remaining_threads,
                 num_threads)
    for i in xrange(remaining_threads):
        alive_threads[i][2].put('STOP')
        #alive_threads[i][2].close()
    logging.debug("Sent STOP requests. Notifying queue that no further "
                  "requests will come.")

    logging.info("All information sent to the threads.")

    # Note end of output

    while len(threads)>0:
        a_thread=threads.pop()
        # We join the process to wait for the end of the reading 
        a_thread[0].join()
        # logging.log(ULTRADEBUG, "Fetching results from finished process.")
        # all_results.update(a_process[1].get()) # Add results to result pool
        # logging.log(ULTRADEBUG, "Received results.")
    logging.info("Finishing writing out results.")
    this_output_queue.put("STOP")
    output_processor.join()
    logging.info("Results written. Finishing multithreading.")
    Pmid.close_storage()
    return

