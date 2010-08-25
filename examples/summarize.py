#!/usr/bin/env python
# encoding: utf-8
"""
summarize.py

Contains a simplistic example of TextRank-based summarization using MEDRank. The
algorithm implemented is described in: 
Mihalcea and Tarau. TextRank: Bringing Order into Texts. Proceedings of the
Conference on Empirical Methods in Natural Language Processing (EMNLP 2004) 

The first parameter to the script should be an input file. The input file should
have ONE SENTENCE PER LINE, SEPARATED WITH CR/LF, CR, OR LF. This example does
not attempt to separate sentences, which is a difficult problem in its own 
right.

The second parameter should be the ratio of sentences desired for the output. 
If unspecified, it will default to 0.2 of the number of original sentences.

Created by Jorge R. Herskovic on 2010-08-25.
Copyright (c) 2010 Jorge Herskovic. All rights reserved.
"""

import sys
import re
import math
from MEDRank.computation.node import Node
from MEDRank.computation.link import AdirectionalLink
from MEDRank.computation.graph import Graph
from MEDRank.computation.textranker import TextRanker
from MEDRank.computation.mapped_ranker import MappedRanker

words=re.compile(r'[a-z]+', re.IGNORECASE)   
      
def sentence_similarity(sentence1, sentence2):
    """Compute a similarity score like Hoopers' indexing consistency, but with 
    ∑ log(length) for a denominator (as in Mihalcea's paper)"""
    w1=[x.lower() for x in words.findall(sentence1)]
    w2=[x.lower() for x in words.findall(sentence2)]
    common=[x for x in w1 if x in w2]
    if len(w1)+len(w2)==0:
        return 0.0
    return float(len(common))/(math.log10(len(w1))+math.log10(len(w2)))
    
def sentence_pairs(sentences):
    pairs=set([])
    for i in xrange(len(sentences)-1):
        for j in xrange(i+1, len(sentences)):
            pairs.add((i,j))
    return pairs
    
def cmp_two_nodes_by_id(n1, n2):
    """Compares two Node instances by their ID, so that a Node with a greater ID
    is greater than a Node with a smaller ID."""
    return cmp(n1.node_id, n2.node_id)
    
def main():
    # Read all lines, stripping trailing newlines and leading spaces
    sentences=[s.strip() for s in open(sys.argv[1], 'rU')]
    
    # Eliminate empty lines
    sentences=[s for s in sentences if len(s)>0]
    # Create one Node per sentence, with a unique ID based on sequential 
    # numbering, the contents of the sentence, and an initial node weight of 1.0
    sentnodes=[Node(x, sentences[x], 1.0) for x in xrange(len(sentences))]
    
    # Create an empty graph
    sentgraph=Graph()
    
    # Compute the similarity between every pair of sentences and add a link to
    # the graph connecting those nodes. THe 
    for p in sentence_pairs(sentences):
        n1, n2=sentnodes[p[0]], sentnodes[p[1]]
        sentlink=AdirectionalLink(n1, n2, 
                                  sentence_similarity(sentences[p[0]],
                                                      sentences[p[1]]))
        sentgraph.add_relationship(sentlink)
        
    # Create a default TextRanker (that implements TextRank as described) and
    # wrap it in the MappedRanker class, which returns (node, score) pairings
    # instead of just scores
    ranker=MappedRanker(TextRanker())
    # Convert the graph to a link matrix
    matrix=sentgraph.as_mapped_link_matrix()
    # Run the ranker on the matrix
    results=ranker.evaluate(matrix)
    # The ranker returns a RankedResultSet that behaves like a list of
    # (node, score) pairings. By default these are sorted in reverse order,
    # i.e., the highest scores at the beginning. To obtain the desired sentences
    # we just trim the list to size.
    try:
        # Try to get a float from the command line
        desired_length=int(round(float(sys.argv[2])*len(sentences)))
    except:
        desired_length=int(round(float(len(sentences))*0.2))

    # For the final output we only need the node, not its score
    shortened_results=[x[0] for x in results]
    # Now we trim it to the desired length
    shortened_results=shortened_results[:desired_length]
    # Now, for presentation purposes, we reorder the truncated list in its 
    # original order.
    shortened_results.sort(cmp=cmp_two_nodes_by_id)
    
    # Output the summary as a paragraph
    print ' '. join([x.name for x in shortened_results])
    
if __name__ == '__main__':
    main()