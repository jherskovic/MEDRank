#!/usr/bin/env python
# encoding: utf-8
"""
get_list_bacteria_names.py

Created by Jorge Herskovic on 2008-11-25.
Copyright (c) 2008 University of Texas - Houston. All rights reserved.
"""

import sys
import os
import urllib2
import re

book_base_url="http://www.ncbi.nlm.nih.gov/bookshelf/br.fcgi?book=bacname&part="
book_index=book_base_url+"part2.bxml"

def retrieve_list_of_pages(list_url, base_url):
    fetch_list=urllib2.urlopen(list_url).read()
    interesting_links=re.compile(r"""[<]a href=["]br[.]fcgi[?]book=bacname[&]amp[;]part=(\w+)["] class=["]new-related-obj["][>][A-Z][<]/a[>]""")
    return [base_url+x for x in interesting_links.findall(fetch_list)]

def retrieve_a_page(page_url):
    return urllib2.urlopen(page_url).read()
    
def extract_all_bacterial_abbreviations(page_text):
    bact=re.compile(r"""[<]p xmlns[:]mml=["]http[:][/][/]www[.]w3[.]org[/]1998[/]Math[/]MathML["] class=["]text-dec bookmain main["] id=["]\w+["][>][<]b[>](?:[<]span class=["]ext-reflink["][>])?(?:[<]a href=["].*?["].*?[>])?([A-Z][.] [a-z]+)""")
    candidates=bact.findall(page_text)
    # make unique
    return set(candidates)
    
def main():
    pages=retrieve_list_of_pages(book_index, book_base_url)
    bacteria=set()
    for page in pages:
        print "Fetching page", page
        page_text=retrieve_a_page(page)
        print "Processing"
        bacteria|=extract_all_bacterial_abbreviations(page_text)
    print "Dumping list of bacteria to", sys.argv[1]
    bacteria_list=list(bacteria)
    bacteria_list.sort()
    open(sys.argv[1], 'w').write('\n'.join(bacteria_list))
    
if __name__ == '__main__':
    main()

