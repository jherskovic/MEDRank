#!/usr/bin/env python
# encoding: utf-8
"""
output.py

Created by Jorge Herskovic on 2010-07-02.
Copyright (c) 2010 University of Texas - Houston. All rights reserved.
"""
from csv import DictWriter
import traceback
import os
from MEDRank.utility import proctitle
from MEDRank.utility.logger import logging, ULTRADEBUG

def output_one_item(output_file, pmid, result, column_names):
    output_writer=DictWriter(output_file, 
                             fieldnames=column_names)
    outdict=result.as_dict()
    # Convert the PMID to string, which will be harmless of it's any
    # datatype but force it to display just the actual number if it's
    # a Pmid()
    outdict['pmid']=str(pmid)
    output_writer.writerow(outdict)
    return
    
def output_headers(output_file, column_names):
    output_writer=DictWriter(output_file, 
                             fieldnames=column_names)
    output_writer.writer.writerow(column_names) 
    return

def output(output_file, result_queue, headers_callback=output_headers, 
           item_callback=output_one_item, initial_result_set_size=100):
    """Actually dumps the result set to output. Override for easy output
    customization."""
    result_set={}
    proctitle.setproctitle("MEDRank-output-processor")
    stop_requested=False
    # Gather a few values
    logging.log(ULTRADEBUG, "Gathering values for initial analysis.")
    for i in xrange(initial_result_set_size):
        logging.log(ULTRADEBUG, "Getting results %d.", i)
        try:
            request=result_queue.get()
            if request=='STOP':
                stop_requested=True
                break
            result_set.update(request)
        except KeyboardInterrupt:
            return
        except:
            logging.warn("EXCEPTION RAISED: \n%s", traceback.format_exc())

    logging.log(ULTRADEBUG, "Values gathered. Computing columns.")
            
    column_names=set([])
    # Add the colnames to the csv
    if headers_callback is not None:
        for result in result_set.itervalues():
            column_names|=result.columns()
        # Create a writer
        column_names=['pmid'] + [x for x in column_names]
        headers_callback(output_file, column_names)
    logging.log(ULTRADEBUG, "Looping to get more results and output them.")
    while True:
        if not stop_requested:
            try:
                request=result_queue.get()
                if request=='STOP':
                    stop_requested=True
                else:
                    result_set.update(request)
            except KeyboardInterrupt:
                return
            except:
                logging.warn("EXCEPTION RAISED: \n%s", traceback.format_exc())
        if stop_requested and len(result_set)==0:
            break
        if len(result_set)==0:
            continue # It can happen! We might get no results, or an empty set.
        pmid=result_set.keys()[0]
        logging.log(ULTRADEBUG, "Output: article %r.", pmid)
        result=result_set[pmid]
        item_callback(output_file, pmid, result, column_names)
        del result_set[pmid]
    output_file.flush()
    try:
        os.fsync(output_file.fileno())
    except:
        logging.warn("Could not fsync the output file. Traceback follows.\n%s",
                     traceback.format_exc())
    return
