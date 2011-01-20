#!/usr/bin/env python
# encoding: utf-8
"""
workflow.py

Contains typical workflows using the system. It's essentially a Facade (see 
Design Patterns p.185)

Created by Jorge Herskovic on 2008-05-27.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""
from MEDRank.utility.logger import logging, ULTRADEBUG
import os
import operator
import sys
import gc
from multiprocessing import (Queue, JoinableQueue, cpu_count, Process, 
                             current_process)
from MEDRank.file.disk_backed_dict import StringDBDict
from MEDRank.umls.concept import Concept
from MEDRank.pubmed.pmid import Pmid
from MEDRank.utility.output import *
from MEDRank.utility import proctitle
from MEDRank.utility.process import processor

# pylint: disable-msg=C0322
        
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
                    num_processes=None,
                    queue_size=None,
                    output_callback=output,
                    output_headers_callback=output_headers,
                    output_item_callback=output_one_item,
                    performance_tuning=True):
    """
    Perform the evaluation.
    Multiprocessing notes: It's the responsibility of the caller to make sure that
    extra_data_contents, if any, are multiprocessing-safe. For example, by using
    a SyncManager and Namespace and passing the proxy. See umls/concept for an example.
    """
    
    if num_processes is None:
        num_processes=cpu_count()

    if performance_tuning:
        # Since reading the file involves an awful lot of object creation 
        # and destruction we'll tweak the gc adjustments to sweep less frequently
        # IOW - we have a LOT of short-lived objects. No sense garbage-collecting
        # the latter generations very often.    
        # (this is about 10x, 5x, and 5x the usual)
        original_threshold=gc.get_threshold()
        gc.set_threshold(10 * original_threshold[0], 
                         5 * original_threshold[1],
                         5 * original_threshold[1]) 
        original_check_interval=sys.getcheckinterval()
        # Similarly, we'll try to minimize overhead from thread switches
        # 5x usual value
        sys.setcheckinterval(5*original_check_interval)
    logging.debug("Initializing Concept storage from %s", 
                  umls_concept_data_filename)
                  
    if umls_concept_data_filename is None:
        Concept.init_storage()
    else:
        Concept.init_storage(StringDBDict(umls_concept_data_filename))
    Pmid.init_storage()

    proctitle.setproctitle("MEDRank-main")
    
    processes=[]
    logging.info("Creating %d worker processes.", num_processes)
    #task_queue=[JoinableQueue(queue_size) for x in xrange(num_processes)]
    task_queues=[Queue(queue_size) for x in xrange(num_processes)]
    this_output_queue=Queue(2*queue_size)

    # Create an output processor
    output_processor=Process(target=output_callback, 
                             args=(output_file, 
                                   this_output_queue,
                                   output_headers_callback,
                                   output_item_callback))
    output_processor.start()
    
    for i in xrange(num_processes):
        this_process=Process(target=processor, args=(workflow_class,
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
                                                this_output_queue,
                                                "MEDRank-Worker-%d" % i),
                             name="MEDRank-Worker-%d" % i)
        logging.log(ULTRADEBUG, "Created process: %r", this_process)
        this_process.start()
        processes.append((this_process, this_output_queue, task_queues[i]))
    
    all_results={}
    count=0

    # Use a single dispatch queue for automagical load balancing
    # CHANGED - Now uses multiple queues to avoid starving due to waiting on semlocks
    for each_article in reader:
        count+=1
        #queues_and_sizes=[(task_queues[x].qsize(), x) 
        #                  for x in xrange(num_processes)]
        #queues_and_sizes.sort()
        #target_process=queues_and_sizes[0][1]
        # logging.info("Dispatching article %d: %r", count, each_article)
        target_process=(count-1) % num_processes
        #Lowest-loaded process first.
        logging.info("Dispatching article %d: %s to %s", 
                     count,
                     each_article.set_id,
                     processes[target_process][0].name)
        task_queues[target_process].put(each_article)
        #task_queue[target_process].put(each_article)
        #task_queue.put(each_article)
        #logging.info("The task queue is approximately %d items long.", 
        #             task_queue.qsize())

    logging.log(ULTRADEBUG, "Waiting for processing to end.")
    all_results={}

    alive_processes=[x for x in processes if x[0].is_alive()]
    remaining_processes=len(alive_processes)

    logging.info("There are %d processes (out of %d) still alive.", 
                 remaining_processes,
                 num_processes)
    for i in xrange(remaining_processes):
        alive_processes[i][2].put('STOP')
        alive_processes[i][2].close()
    logging.debug("Sent STOP requests. Notifying queue that no further "
                  "requests will come.")

    logging.info("All information sent to the processors.")

    # Back to normal
    if performance_tuning:
        gc.set_threshold(original_threshold[0],
                         original_threshold[1],
                         original_threshold[2])
        sys.setcheckinterval(original_check_interval)

    # Note end of output

    while len(processes)>0:
        a_process=processes.pop()
        # We join the process to wait for the end of the reading 
        a_process[0].join()
        # logging.log(ULTRADEBUG, "Fetching results from finished process.")
        # all_results.update(a_process[1].get()) # Add results to result pool
        # logging.log(ULTRADEBUG, "Received results.")
    logging.info("Finishing writing out results.")
    this_output_queue.put("STOP")
    output_processor.join()
    logging.info("Results written. Finishing multiprocessing.")
    return

