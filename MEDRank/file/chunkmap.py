#!/usr/bin/env python
# encoding: utf-8
""" chunkmap.py

A chunkmap is a file that describes the split an article goes through before
being processed by the NLP tools. We must split long articles into shorter
'chunks' of text because most NLP tools (at least the NLM ones, and BioMedLEE)
can't deal with long, unbroken pieces of text. It may also be advantageous to
split some texts into logical subunits like sentences or paragraphs for
certain tasks.

Chunkmaps have certain associated ugliness because I retain backwards
compatibility with MEDRank V1, whose chunkmaps were all over the place. There
were actually two different kinds of chunkmap: 1. Article text->many chunks 2.
Article text->single chunk, tagged with the PubMed ID (the second kind is used
by the applications that handle only abstracts)

Chunkmaps should always be created (on loading) by their factory method, which
can interpret and build the proper type. The factory is chunkmap_factory, and
it should be called with the original dictionary as an argument.

The important operation for any kind of chunkmap is pmid_from_block, which
always returns a PubMed ID (as defined in pubmed/pmid.py) when given a chunk
number.

Created by Jorge Herskovic on 2008-05-13. 
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""
import re
from MEDRank.utility.logger import logging, ULTRADEBUG

# pylint: disable-msg=F0401
from MEDRank.pubmed.pmid import Pmid

class BaseChunkmap(dict):
    def __init__(self, original_dictionary):
        """Creates a chunkmap based on a dictionary (for V1 backwards
        compatibility)"""
        dict.__init__(self)
        self.update(original_dictionary)
        self._reverse_chunkmap={} # To be filled in by derived classes
    def pmid_from_block(self, chunknum):
        """Returns the PMID that corresponds to a chunk."""
        return self._reverse_chunkmap[chunknum]

class OriginalChunkmap(BaseChunkmap):
    def __init__(self, original_dictionary):
        BaseChunkmap.__init__(self, original_dictionary)
        logging.log(ULTRADEBUG, "Creating OriginalChunkmap")
        self.fill_in_reverse_chunkmap()
    def fill_in_reverse_chunkmap(self):
        """Creates a reverse chunkmap. The original chunkmap holds a
        filename->[chunk ids] map. We want to turn this into a chunk id->
        pubmed id map. In order to do that, we extract the pubmed id from
        each and add the chunkids as new keys to the reverse dictionary, with
        the pubmed id as default value."""
        for k, value in self.iteritems():
            pubmed_id=Pmid()
            pubmed_id.set_from_string(k)
            chunk_ids=[int(x) for x in value]
            self._reverse_chunkmap.update(
                dict.fromkeys(chunk_ids, pubmed_id))

class UselessChunkmap(BaseChunkmap):
    """How else would you call a chunkmap that maps things to themselves?"""
    def __init__(self, original_dictionary):
        BaseChunkmap.__init__(self, original_dictionary)
        logging.log(ULTRADEBUG, "Creating UselessChunkmap")
    def pmid_from_block(self, chunknum):
        return Pmid(self[chunknum])
    
class FakeChunkmap(BaseChunkmap): 
    def __init__(self):
        BaseChunkmap.__init__(self, {})
        self._number_finder=re.compile(r'\d+')
    def pmid_from_block(self, chunknum):
        num=self._number_finder.findall(str(chunknum))
        if len(num) == 0:
            raise KeyError("No chunk number found in %r" % chunknum)
        return Pmid(num[0])
    
def guess_chunkmap_type(a_dictionary):
    """Takes an educated guess at what type of chunkmap a dictionary is."""
    return OriginalChunkmap if isinstance(a_dictionary.keys()[0], str) \
        else UselessChunkmap

def chunkmap_factory(a_dictionary):
    """Guesses the type of chunkmap, based on the dictionary, and returns the
    proper chunkmap instance."""
    return guess_chunkmap_type(a_dictionary)(a_dictionary)
