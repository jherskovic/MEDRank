#!/usr/bin/env python
# encoding: utf-8
"""
semantic_predications.py

Reads a semantic predication file (produced by Dr. Trevor Cohen's software) and
produces Links and Nodes based on it. Semantic predication files are pretty
straightforward XML. The parts that interest us are:

<ARTICLE pmid = 1>
<CUIS>
C1
C2
C3
</CUIS>
<NAMES>
Concept1
Concept2
Concept3
</NAMES>
<CONNECTIVITIES>
0, 1, 2
1, 0, 3
2, 3, 0
</CONNECTIVITIES>
<RELATIONS>
null, DISRUPTS?, COMPLICATES?
DISRUPTS?, null, MEASURES?
COMPLICATES?, MEASURES?, null
</RELATIONS>
</ARTICLE>

So there's one item per line under CUIS, and each line under CONNECTIVITIES and
RELATIONS is a row of a matrix whose elements are the previously-mentioned CUIs.
These describe the kind of relation and the strength of the connection between
the concepts.
"""

from MEDRank.computation.node import Node
from MEDRank.computation.link import Link
from MEDRank.utility import cache
import sys
import re
import os.path
import bz2
import cPickle as pickle

current_element=None
current_article=None
current_cuis=None
current_names=None
current_nodes=None
current_relations=None
current_strengths=None
current_links=None
current_content=[]
article_handler=re.compile(r"\<\s*article\s*pmid\s*\=\s*(\w+)\s*\>",
                           re.IGNORECASE)
known_opening_tags=re.compile(r"\<(cuis|names|connectivities|relations)\>",
                              re.IGNORECASE)
known_closing_tags=re.compile(r"\</(cuis|names|connectivities|relations)\>",
                              re.IGNORECASE)
SEMPRED_CACHE=os.path.join(cache.path(), "sempred")
                              
def get_predications(pubmed_id, path=SEMPRED_CACHE):
    filename=os.path.join(path, "%d.pickle.bz2" % pubmed_id)
    return pickle.load(bz2.BZ2File(filename))
                              
def handle_cuis(data):
    return [x.strip().lower() for x in data]

def handle_names(data):
    return [x.strip().lower() for x in data]
    
def handle_connectivities(data, nodes):
    relations={}
    line=0
    for l in data:
        concept=0
        from_concept=nodes[line]
        for c in l.split(','):
            try:
                this_strength=float(c)
            except ValueError:
                print "There should've been a float here:", l,
                print "At position", line, ",", concept
                print "There are", len(current_nodes), "nodes"
            to_concept=nodes[concept]
            relations[(from_concept, to_concept)]=this_strength
            concept+=1
        line+=1
    return relations
  
def handle_relations(data, nodes):
    relations={}
    line=0
    for l in data:
        concept=0
        from_concept=nodes[line]
        for c in l.split(','):
            this_relation=c.strip().lower()
            to_concept=nodes[concept]
            relations[(from_concept, to_concept)]=this_relation
            concept+=1
        line+=1
    return relations

def make_links(strengths, relations, epsilon=1e-10):
    # Eliminates links with a strength < epsilon
    links={}
    if relations is None:
        relations={}
    for k, v in strengths.iteritems():
        if abs(v)>epsilon:
            # Don't create links for 0-strength relationships.
            # HOWEVER, some versions only have connectivities. If that is the case,
            # then don't check for null relations.
            if len(relations)>0 and relations[k]=='null':
                print "Relation",k,"is null but has strength",v
                continue
            links[k]=Link(k[0], k[1], v, relations.get(k, "UNK"))
    return links
        
def complete_record_handler(article_number, links):
    print "Article=", article_number, "parsed successfully.", len(links),\
          "links found."
    #print "Links=", links
        
def end_element(name, record_callback):
    global current_links
    global current_element
    global current_article
    global current_cuis
    global current_names
    global current_nodes
    global current_relations
    global current_strengths
    global current_links
    global current_content
    
    data=''.join(current_content)
    data=[x for x in data.splitlines() if len(x)>0]
    name=name.strip().lower()
    
    if name=='cuis':
        current_cuis=handle_cuis(data)
    if name=='names':
        current_names=handle_names(data)
    if name=='connectivities':
        current_strengths=handle_connectivities(data, current_nodes)
    if current_cuis is not None and current_names is not None:
        current_nodes=[Node(x[0], x[1], 1) 
                       for x in zip(current_cuis, current_names)]
    if name=='relations':
        current_relations=handle_relations(data, current_nodes)
    # Very inefficient if there are, in fact, relations, but if they aren't this
    # will make it actually work.
    if current_strengths is not None:
        current_links=make_links(current_strengths, current_relations)
        # Free some memory
        current_strengths=None
        current_relations=None

    if name=='article':
        record_callback(current_article, current_links)
        current_element=None
        current_article=None
        current_cuis=None
        current_names=None
        current_nodes=None
        current_relations=None
        current_strengths=None
        current_links=None
    current_content=[]
        
def parse_xml(a_file, record_callback=complete_record_handler):
    # Simulates a real XML parser to deal with the quasi-XML we get from SemPred
    # Part of the weirdness here will come from repurposing the code I already
    # wrote for expat.
    """Parses an XML file produced by Semantic Predications. It doesn't 
    actually have to be a file; any object that iterates line by line is OK.
    Please also pass a record callback that knows how to handle the records. 
    The prototype is record_callback(pubmed_id_number, list_of_links)
    The links will have their name set to the relationship returned by the
    Semantic Predications software, and their strength set to whatever the
    Sem Pred software says.
    """
    
    global current_element
    global current_article
    global current_content
    
    in_article=False
    in_tag=False
    # Go line by line
    for l in a_file:
        article_number=article_handler.findall(l)
        if len(article_number)>0 and not in_article:
            in_article=True
            current_article=int(article_number[0])
        if not in_article:
            continue
        lower_l=l.lower()
        if "</article>" in lower_l:
            end_element('article', record_callback)
            in_article=False
            continue
        if not in_tag:
            tag=known_opening_tags.findall(lower_l)
            if len(tag)>0:
                in_tag=True
                current_element=tag[0]
        else:
            tag=known_closing_tags.findall(lower_l)
            if len(tag)>0:
                in_tag=False
                end_element(tag[0], record_callback)
            else:
                current_content.append(l)
                
def main(filename=None):
    if filename is None:
        filename=sys.argv[1]
    parse_xml(open(filename))
    
if __name__=="__main__":
    main()
