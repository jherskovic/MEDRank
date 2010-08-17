#!/usr/bin/env python
# encoding: utf-8
"""
tf_idf.py

Creates and mantains a TF*IDF dictionary from a file reader. Since it consumes
the iterator, the file will have to be opened twice.

It will build the dictionary in memory for speed, and keep it in RAM.

It will blindly include ANY line that has a CUI, using its confidence as the value. 

Created by Jorge Herskovic on 2008-06-11.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

from MEDRank.utility.logger import logging
import os.path
import cPickle as pickle
import bz2
import math
from MEDRank.file.disk_backed_dict import StringDBDict

class TF_IDF(dict):
    """The values in this dictionary measure how common terms are."""
    def cache_file_name(self, original_filename):
        """Creates a filename for the cache based on the filename of the 
        original file. Deterministically."""
        filepath, name=os.path.split(original_filename)
        if name[0]!='.':
            name='.'+name
        name+='.tfidf.cache'
        return os.path.join(filepath, name)
    def populate_from_cache(self, cache_filename):
        cache_list=pickle.load(bz2.BZ2File(cache_filename))
        for k, v in cache_list:
            self[k]=v
        return
    def dump_to_cache(self, cache_filename):
        cache_list=[x for x in self.iteritems()]
        pickle.dump(cache_list, bz2.BZ2File(cache_filename, 'w'),
                    pickle.HIGHEST_PROTOCOL)
        return
    def build_idf_from_file(self, file_reader, default_score=None):
        tempdict={}
        logging.info("Building the term frequency dictionary")
        count=1
        logging.debug("Checking for a cache file, and loading from it.")
        try:
            self.populate_from_cache(
                self.cache_file_name(file_reader.original_file.name))
            logging.info("Loaded from cache. It's not necessary to build.")
            return
        except:
            logging.debug("Nope. Proceeding with building the dictionary.")
        for article in file_reader:
            logging.debug("Processing article %r (number %d) for the term"
                         " frequency dictionary", article, count)
            if article.set_id.pmid < 0:
                logging.warn("Article with unknown PubMed ID - skipping")
                continue
            count+=1
            tempcounts={}
            for line in article.lines:
                try:
                    this_cui=line.CUI
                except AttributeError:
                    continue
                # Use the confidence as the score if no default is specified
                #if default_score is None:
                #    try:
                #        this_score=line.confidence
                #    except AttributeError:
                #        continue
                #else:
                #    this_score=default_score
                #tempdict[this_cui]=tempdict.get(this_cui, 0.0)+this_score
                tempcounts[this_cui]=1
            # Now have all the CUIs that appeared in the article. Update
            # the total counts.
            for k in tempcounts:
                tempdict[k]=tempdict.get(k, 0)+1
        logging.debug("Built a dictionary with %d items. Computing IDFs.",
                      len(tempdict))
        # max_value=max(tempdict.itervalues())
        #logging.debug("Saving it to permanent storage.")
        for k, v in tempdict.iteritems():
            self[k]=math.log(count/float(v))+1.0
        logging.info("Done building the dictionary. Dumping it to a cache "
                     "file.")
        self.dump_to_cache(
                self.cache_file_name(file_reader.original_file.name))
        return
    def start_tf(self):
        """Erase internal counters to set up for a TF*IDF computation"""
        self.document_dict={}
    def tf_line(self, line):
        """Add a line (if possible) to the TF."""
        try:
            this_cui=line.CUI
        except AttributeError:
            return
        self.document_dict[this_cui]=self.document_dict.get(this_cui,0)+1
        return
    def end_tf(self):
        """Returns a TF*IDF dictionary with the weights of each term"""
        # Normalize the dictionary
        relative_values={}
        for k, v in self.document_dict.iteritems():
            relative_values[k]=(math.log(v)+1.0)*self[k] # Multiplying by the
                                         # inverse of the term in doc freq
        # Normalization
        #max_value=max(relative_values.itervalues())
        #for k, v in relative_values.iteritems():
        #    relative_values[k]=v/max_value # Normalization
        return relative_values

    