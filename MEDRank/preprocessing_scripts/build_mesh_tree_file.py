#!/usr/bin/env python
"""Reads the original NLM MeSH files and builds a MeSH tree, storing it in a
   DBDict for posterior use.
   The first argument should be the desired name of the tree file, the rest
   should be BZ2 compressed files that contain the NLM data (in .bin
   format)"""
import sys
import copy
import bz2
from MEDRank.utility.logger import logging
from MEDRank.mesh.tree_node import TreeNode
from MEDRank.file.disk_backed_dict import StringDBDict
# I hope you have psyco
#try:
#    import psyco
#    psyco.full()
#except ImportError:
#    pass
    
def build_tree_from_descriptor_file(treefile, trees={}):
    def read_one_record(from_file):
        """Swallows a record from a file, returns a dictionary of
        key: [list of values]
        as each variable in a MEDLINE record can have more than one value.
        Stores them in whatever you pass as "trees"
        """
        # Gobble record first
        current_record={}
        reading_record=False
        for l in from_file:
            l=l.strip()
            # Eat leading whitespace if necessary, but if we're reading a
            # record already, a blank line signals the end.
            if reading_record:
                if l=='': 
                    #logging.debug('Record=%s', str(current_record))
                    return current_record
                # Any other '=' belongs in value
                variable,value=l.split('=', 1) 
                variable=variable.strip().lower()
                value=value.strip()
                if variable in current_record:
                    current_record[variable].append(value)
                else:
                    current_record[variable]=[value]
            else:
                if l=='*NEWRECORD':
                    reading_record=True
                    continue
        from_file.close() # This way we'll be able to end the iteration
        return current_record

    while True:
        if treefile.closed: break
        rec=read_one_record(treefile)
        if len(rec)==0: break
        synonyms=[]
        if rec['rectype'][0]=='D':
            # Descriptor record
            term=rec['mh'][0].lower()
            role='mh'
            synonyms=[x.split('|')[0] for x in rec.get('entry', [])]
            synonyms+=[x.split('|')[0] for x in rec.get('print entry', [])]
        elif rec['rectype'][0]=='Q':
            # Qualifier record
            term=rec['sh'][0].lower()
            role='sh'
        elif rec['rectype'][0]=='C':
            # Supplementary concept
            term=rec['nm'][0].lower()
            role='sc'
        else:
            logging.debug('Unknown record type %s, assuming Descriptor', 
                          rec['rectype'][0])
            term=rec['mh'][0].lower()
            role='mh?'
        logging.debug('Processing %s', term)
        # The following lines deal with records with a MeSH tree number
        # (i.e. checktags, qualifiers)
        if 'mn' in rec:
            position=rec['mn']
        else:
            position=rec['ui'] # Unique identifier
        if term in trees:
            trees[term].position|=set(position)
        else:
            trees[term]=TreeNode(term, role, synonyms, set(position))
    return trees


if __name__=="__main__":
    # The pickling and unpickling make this horribly slow, so we'll trade some
    # memory for speed in the build process and later turn the dictionary into
    # a DB-backed one.
    tree_storage={}
    for treefile in sys.argv[2:]:
        treesfile=bz2.BZ2File(treefile, 'rU')
        print "Reading %s..." % treefile
        tree_storage=build_tree_from_descriptor_file(treesfile, tree_storage)
    
    print "Tree built. It has %d unique terms." % len(tree_storage)
    print "For example... arm=", tree_storage['arm'], " and eye=", \
          tree_storage['eye']
    print "Done generating tree."
    print "Storing tree in", sys.argv[1]
    tree_on_disk=StringDBDict(persistent_file=sys.argv[1], 
                              sync_every_transactions=0,
                              write_out_every_transactions=0,
                              file_mode='c')
    write_counter=0
    for k,v in tree_storage.iteritems():
        tree_on_disk[k]=v
        write_counter+=1
        if write_counter % 1000 == 0:
            print "Stored", write_counter, "terms."
    tree_on_disk.sync_every=1
    print "Done storing."