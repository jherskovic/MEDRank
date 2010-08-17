#!/usr/bin/env python
# encoding: utf-8
"""
process.py

Created by Jorge Herskovic on 2010-07-02.
Copyright (c) 2010 University of Texas - Houston. All rights reserved.
"""

from MEDRank.utility import proctitle
from MEDRank.utility.logger import logging, ULTRADEBUG
from MEDRank.utility.workflow import CouldNotRank
import traceback
# pylint: disable-msg=C0322

def processor(workflow_class,
              graph_builder_constructor, graph_builder_params,
              ranker_constructor, ranker_params,
              eval_parameters, 
              ranking_cutoff,
              mesh_tree_filename, distance_matrix_filename,
              distance_function,
              umls_converter_data_filename,
              extra_data_name,
              extra_data_contents,
              my_input_queue, my_output_queue,
              my_own_name=None):
    logging.info("Setting up worker.")
    if my_own_name is not None:
        proctitle.setproctitle(my_own_name)

    my_workflow=workflow_class(graph_builder_constructor,
                               graph_builder_params,
                               ranker_constructor,
                               ranker_params,
                               eval_parameters,
                               ranking_cutoff,
                               mesh_tree_filename,
                               distance_matrix_filename,
                               distance_function,
                               umls_converter_data_filename
                               )
    if extra_data_name is not None:
        my_workflow.__setattr__(extra_data_name, extra_data_contents)
    logging.info("Finished setting up worker process. Waiting for requests.")
    try:
        while True:
            request=my_input_queue.get()
            logging.log(ULTRADEBUG, "Processing request %r", request)
            if request=='STOP':
                logging.log(ULTRADEBUG, "Received stop request.")
                break
            try:
                my_workflow.process_article(request)
                # Recover the article, push it on the output queue
                my_output_queue.put(my_workflow.all_results)
                # Clear the output queue
                my_workflow.all_results={}
            except CouldNotRank:
                #my_input_queue.put(request) # On error, push the task
                                            # back into the queue
                logging.info("Skipping unrankable article.")
            except:
                logging.warn("EXCEPTION RAISED: \n%s", 
                             traceback.format_exc())
                raise
    finally:
        logging.log(ULTRADEBUG, "Returning results to caller.")
        logging.log(ULTRADEBUG, "Ending processor execution.")
    return
