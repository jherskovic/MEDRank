#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

"""
Prepares a set of articles for submission to the NLM
©2008 Jorge Herskovic

Gets the original Pubmed Central .tar.gz files, extracts the article text, bundles it into a submission file and a chunkmap. Also retrieves the PubMed articles, primes the pubmed article cache with them, and prepares the MTI submission file. 

This script was derived from several MEDRank V1 separate scripts. It will be functional, but ugly.

Arguments:
    output_file cache_file_to_prime list_of_bacteria_file [--title-abstract]
    
    if the fourth argument is present, it will include titles and abstracts in the
    output.

Run it in the directory that contains the sample.
"""

import sys, re, tarfile, glob, os.path, operator, cPickle as pickle
from xml.dom.minidom import parse
from Bio import PubMed, Medline
from MEDRank.file.disk_backed_dict import StringDBDict
from MEDRank.pubmed.pmid import DEFAULT_CACHE_NAME

try:
    import psyco
    psyco.full()
except ImportError: 
    pass
        
def find_xml_file_handle_in_tarball(tarball_name):
    tarball=tarfile.open(tarball_name) # Defaults to automatic compression handling, which is very nice
    short_list=[x for x in tarball.getnames() if '.nxml' in x]
    if len(short_list) != 1:
        raise IndexError('I expected exactly one .nxml file inside the tarball, yet there are %d.' % len(short_list))
    the_filename=short_list[0]
    return tarball.extractfile(the_filename)

def clean_extracted_unicode(text,
                    citationer=re.compile(r'\[.*?\]', re.MULTILINE),
                    unicoder=re.compile(r'\\u[0-9a-f]{4}', re.MULTILINE)):
    outtext=citationer.sub('', text)
    return unicoder.sub('', outtext)

def get_text_from_dom(dom1, 
                      desired_tag=u'article', 
                      desired_part=u'body', 
                      actual_text_in=u'p'):
    outtext=u''
    article_body=dom1.getElementsByTagName(desired_tag)[0].\
                      getElementsByTagName(desired_part)[0]
    for n in article_body.childNodes:
        for t in n.getElementsByTagName(actual_text_in):
            for tt in t.childNodes:
                if tt.nodeType == tt.TEXT_NODE:
                    outtext += unicode.encode(tt.data, 'unicode_escape')
    return clean_extracted_unicode(outtext)

def get_title_from_dom(dom1, 
                       title_tag=u'article-meta',
                       title_group=u'title-group',
                       actual_text_in=u'article-title'):
    title=[unicode.encode(x.data, 'unicode_escape') for x in
           dom1.getElementsByTagName(title_tag)[0].\
           getElementsByTagName(title_group)[0].\
           getElementsByTagName(actual_text_in)[0].childNodes
           if x.nodeType==x.TEXT_NODE]
    return clean_extracted_unicode(' '.join(title))

def format_medline_field(field_code, contents, max_width=80):
    def word_wrapper(a_string, column_size):
        words=[x.strip() for x in a_string.split()]
        if len(words)==0: return ['']
        lines=[]
        this_line=words[0]
        for word in words[1:]:
            tentative_line=this_line+" "+word
            if len(tentative_line)>column_size:
                lines.append(this_line)
                this_line=word
            else:
                this_line=tentative_line
        if this_line!="":
            lines.append(this_line)
        return lines
    first_line_template="%2.2s  - %s\n"
    other_lines_template="      %s\n"
    #other_lines_template=first_line_template % (field_code, r"%s")
    max_internal_width=max_width-5 # Make space for the left column
    lines=word_wrapper(contents, max_internal_width)
    outtext=first_line_template % (field_code, lines[0])
    for line in lines[1:]:
        outtext+=other_lines_template % line
    return outtext

#def get_title_and_abstract_from_dom(dom1):
#    outtext=u''
#    article_title=dom1.getElementsByTagName(u'article-meta')[0].getElementsByTagName(u'article-title')[0]
#    title_text=u''
#    for n in article_title.childNodes:
#        if n.nodeType == n.TEXT_NODE:
#            title_text+=unicode.encode(n.data, 'unicode_escape').strip()
#    #outtext+=format_medline_field('TI', title_text)
#    abstract_text=u''
#    abstract_root=dom1.getElementsByTagName(u'article-meta')[0].getElementsByTagName(u'abstract')[0]
#    for n in abstract_root.childNodes:
#        for t in n.getElementsByTagName(u'p'):
#            for tt in t.childNodes:
#                if tt.nodeType == tt.TEXT_NODE:
#                    abstract_text+=unicode.encode(tt.data, 'unicode_escape').strip()
#    #outtext+=format_medline_field('AB', abstract_text)
#    replacer=re.compile(r'\\u[0-9a-f]{4}', re.MULTILINE)
#    title_text=replacer.sub('', title_text)
#    abstract_text=replacer.sub('', abstract_text)
#    return {'title': title_text, 'abstract': abstract_text}

def get_title_and_abstract_from_dom(dom1):
    title=get_title_from_dom(dom1)
    abstract=get_text_from_dom(dom1, desired_tag=u'article-meta', 
                                     desired_part=u'abstract')
    return {'title': title, 'abstract': abstract}
    
def get_pmid_from_dom(dom1):
    art_ids=dom1.getElementsByTagName('article-id')
    for n in art_ids:
        if n.getAttribute('pub-id-type') == u'pmid':
            # Got a pubmed ID!
            return int(n.childNodes[0].data)
    return None
    
def cleanup(tarballname):
    the_dom=parse(find_xml_file_handle_in_tarball(tarballname))
    pmid=get_pmid_from_dom(the_dom)
    dom_text=""
    if pmid is None:
        print "OOOPS! No PubMed ID for this article."
    else:
        try:
            dom_text=get_text_from_dom(the_dom)
        except:
            dom_text=""
    
        if dom_text == "":
            print "OOPS! No recognizable text in article %d." % pmid
        else:
            return (pmid, dom_text)
    return None

def cleanup_with_abstract_and_title(tarballname):
    the_dom=parse(find_xml_file_handle_in_tarball(tarballname))
    pmid=get_pmid_from_dom(the_dom)
    dom_text=""
    if pmid is None:
        print "OOOPS! No PubMed ID for this article."
    else:
        try:
            a_t=get_title_and_abstract_from_dom(the_dom)
            # The title needs to end with a period to be separated from the 
            # abstract
            dom_text=a_t['title']+'.\n\n'+a_t['abstract']+'\n\n'+\
                     get_text_from_dom(the_dom)
        except:
            dom_text=""
    
        if dom_text == "":
            print "OOPS! No recognizable text in article %d." % pmid
        else:
            return (pmid, dom_text)
    return None
    
#   
# This needs to be a global variable due to the callback mechanism that
# PubMed.download_many uses
the_cache=None

def download_callback(pubmed_id, pubmed_record):
    """docstring for download_callback"""
    global the_cache
    the_cache[pubmed_id]=pubmed_record
    if len(the_cache) % 200 == 0:
        print len(the_cache), "article records downloaded."
    return

def generate_bacteria_token_dictionary(bacterial_names):
    token="%%%%BACTERIAL%%TOKEN_%d%%%%"
    tokendict={}
    revtokendict={}
    for i in range(len(bacterial_names)):
        tokendict[bacterial_names[i]]=token % i
        revtokendict[token % i]=bacterial_names[i]
    return (tokendict, revtokendict)
    
if __name__=="__main__":
    # Works on the .tar.gz files in the current directory
    files_to_work_on=glob.glob('*.tar.gz')
    outfilename=sys.argv[1] + '.metamap'
    outmapname=outfilename+'.chunkmap'
    print "Output goes to", outfilename, "and", outmapname
    print "Cache file in", sys.argv[2], "will get primed"
    try:
        if sys.argv[4]=='--title-abstract':
            print "Getting A&T"
            cleaner_upper=cleanup_with_abstract_and_title
        else:
            cleaner_upper=cleanup
    except:
        print "Failed while setting cleaner_upper. Why?"
        cleaner_upper=cleanup
    outfile=open(outfilename, 'w')
    known_articles=[]
    skipped=[]
    chunkmap={}
    chunkid=0
    cleanuptronic=re.compile(r'[\\]n|[\\]t')
    sepatronic=re.compile(
      r'(?!e[.]g|Eq|eq|fig|Fig|vs|Vs|VS|eq|Eq|EQ|exp|Exp|EXP|al|Al|r[.]m[.]s|'
       '[.][.])([.])\s?([\nA-Z])'
       '(?!coli|Coli|typhi|Typhi|tyhpimurium|Typhimurium|and|[,\)\]\'\"])',
      re.MULTILINE)
    useless_lines=['click here for file', 
                   'courtesy of dr',
                   'reprinted from ref'
                  ]
    bact_tok, tok_bact=generate_bacteria_token_dictionary(
                open(sys.argv[3], 'rU').read().split())
    file_count=0
    for each_file in files_to_work_on:
        # Extract the text from the XML file nested in the tarball
        file_count+=1
        print "Working on", each_file,
        try:
            pmid, article_text=cleaner_upper(each_file)
        except IOError:
            print "but there was a read error. Skipping it."
            skipped.append(each_file)
            continue
        except TypeError:
            print "but there was a read error. Skipping it."
            skipped.append(each_file)
            continue
            
        print "(%d of %d). PMID is" % (file_count, len(files_to_work_on)), \
                pmid
        known_articles.append(pmid)
        # For historical reasons, chunkmaps have filenames
        fakename="%d.txt" % pmid
        chunkmap[fakename]=[]
        article_text=cleanuptronic.sub('', article_text)
        for k, v in bact_tok.iteritems():
            article_text=article_text.replace(k, v)
        these_chunks=sepatronic.sub(r'\n\2', 
                                    article_text.replace(
                                        '\n', '')).split('\n')
        for chunk in these_chunks:
            chunk=chunk.strip()
            for k, v in tok_bact.iteritems():
                chunk=chunk.replace(k, v)
            if reduce(operator.or_, 
                      [x in chunk.lower() for x in useless_lines]): continue
            if len(chunk) < 2: continue
            outfile.write('%010d|%s\n' % (chunkid, chunk))
            chunkmap[fakename].append(chunkid)
            chunkid += 1
    outfile.close()
    print "Saving chunkmap"
    pickle.dump(chunkmap, open(outmapname, "wb"), pickle.HIGHEST_PROTOCOL)
    print "These files couldn't be processed:"
    print '\n'.join(skipped)
    print "Opening (or creating) cache in", sys.argv[2]
    the_cache=StringDBDict(os.path.join(sys.argv[2], DEFAULT_CACHE_NAME),
                           file_mode='c')
    PubMed.download_many([str(x) for x in known_articles if str(x) not in 
                          the_cache.keys()], download_callback,
                         parser=Medline.RecordParser())
    mti_filename=sys.argv[1]+'.mti'
    print "Finished processing the cache. Using the cache to build", \
           mti_filename
    mti_file=open(mti_filename, "w")
    chunkmap={}
    hexfinder=re.compile(r'\\x[a-f0-9][a-f0-9]', re.IGNORECASE)
    for article in known_articles:
        try:
            article_record=the_cache[str(article)]
        except KeyError:
            print "Article doesn't exist in cache. Skipping."
            continue
        if article_record.abstract=='':
            print "Article", article, "has no abstract. Skipping."
            continue
        this_file=format_medline_field('UI', str(article)) + \
                  format_medline_field('TI', article_record.title) + \
                  format_medline_field('AB', article_record.abstract)
        chunkmap[int(article)]=int(article)
        this_file=this_file.replace(r"\n",' ')
        this_file=this_file.replace(r"\t",' ')
        this_file=this_file.replace('\t', ' ')
        this_file=this_file.replace('\n\n', '\n')
        candidate_replacements=hexfinder.findall(this_file)
        unique_replacements=dict.fromkeys(candidate_replacements)
        for rep in unique_replacements:
            repchar=chr(int(rep[2:], 16))
            if ord(repchar) > 127:
                # Non-ascii. Eliminate.
                repchar=' '
            this_file=this_file.replace(rep, repchar)
        mti_file.write('%s\n' % this_file)
    mti_file.close()
    print "Done. Dumping MTI chunkmap."
    pickle.dump(chunkmap, open(mti_filename + '.chunkmap', 'wb'),
                pickle.HIGHEST_PROTOCOL)
    print "Finished all processing."
