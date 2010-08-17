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
from csv import DictWriter
import cPickle as pickle
import ConfigParser
from MEDRank.mesh.tree import Tree
from MEDRank.file.disk_backed_dict import StringDBDict
from MEDRank.evaluation.savcc_normalized_matrix import SavccNormalizedMatrix
from MEDRank.computation.mapped_ranker import MappedRanker
from MEDRank.umls.converter import Converter
from MEDRank.umls.ranked_converter import RankedConverter
from MEDRank.umls.concept import Concept
from MEDRank.mesh.expression import ExpressionList
from MEDRank.evaluation.common import comprehensive
from MEDRank.evaluation.recall import TotalRecall
from MEDRank.evaluation.named_result_set import NamedResultSet
#import time

class CouldNotRank(Exception):
    """Exception signaling that an article could not be ranked."""
    pass
    
class Workflow(object):
    """Contains a basic workflow through the system. The parameters are:
    reader: an instance of an NLMOutput descendant (that knows how to read an
            output file, basically)
    graph_builder: a graph builder
    ranker: a Ranker 
    eval_parameters: Pass an instance of EvaluationParameters, but just fill
                     in the numerical ones. The matrix and tree will be 
                     instantiated and loaded by the Workflow constructor.
    mesh_tree_filename: a filename containing the tree you want to use
    distance_matrix_filename: the distance matrix you wish to use for SAVCC
                              computations
    distance_function:  the distance function used to interpret the distance
                        matrix
    umls_converter_data_filename: a filename pointing to the file built by
                                  the preprocess_checktag_boost_lists.sh 
                                  script
    umls_concept_data_filename: a filename pointing to the file built by the
                                preprocess_umls_mesh_mappings.sh script                            
    output_file: a file object in which you want to place the results of the
                 computation
    Call the run() method to execute it."""
    def __init__(self, reader, graph_builder, ranker, eval_parameters, 
                 ranking_cutoff,
                 mesh_tree_filename, distance_matrix_filename,
                 distance_function,
                 umls_converter_data_filename, umls_concept_data_filename,
                 output_file):
        logging.debug("Setting up a Workflow instance.")
        logging.debug("My reader is: %r", reader)
        self._reader=reader
        logging.debug("My graph builder is: %r", graph_builder)
        self._graph_builder=graph_builder
        self._ranker=MappedRanker(ranker)
        logging.debug("My ranker is: %r", self._ranker)
        self._ranking_cutoff=ranking_cutoff
        logging.debug("My ranking cutoff is: %r", self._ranking_cutoff)
        logging.debug("Creating a Tree instance from %s", mesh_tree_filename)
        self._mesh_tree=Tree(mesh_tree_filename)
        logging.debug("Creating SAVCC distance matrix with %r and distance "
                      "function %r", 
                      distance_matrix_filename, distance_function)
        self._matrix=SavccNormalizedMatrix(
                      open(distance_matrix_filename, "rb"), distance_function)
        logging.debug("Filling in the rest of the evaluation parameters.")
        self._eval_parameters=eval_parameters
        self._eval_parameters.mesh_tree=self._mesh_tree
        self._eval_parameters.savcc_matrix=self._matrix
        logging.debug("My evaluation parameters are: %r", 
                      self._eval_parameters)
        if umls_converter_data_filename is None:
            converter_data=None
        else:
            converter_data=pickle.load(open(umls_converter_data_filename, 
                                            "rb"))
        self._umls_converter=RankedConverter(Converter(self._mesh_tree, 
                                                       converter_data))
        logging.debug("My converter is: %r", self._umls_converter)
        logging.debug("Initializing Concept storage from %s", 
                      umls_concept_data_filename)
        if umls_concept_data_filename is None:
            Concept.init_storage()
        else:
            Concept.init_storage(StringDBDict(umls_concept_data_filename))
        self._output_file=output_file
        logging.debug("My output file is: %r", self._output_file)
        return
    def __repr__(self):
        return "<%s instance>" % self.__class__.__name__
    def limit_length(self, gold_standard_terms, generated_terms):
        """Limits the length of the generated terms and returns the new list.
        By default it just truncates the list to the length of the gold 
        standard. Override to customize."""
        return generated_terms[:len(gold_standard_terms)]
    def create_evaluator(self):
        """Creates and returns the evaluator we'll use - override for easy
        customization"""
        return comprehensive(self._eval_parameters)
    def output(self, result_set):
        """Actually dumps the result set to output. Override for easy output
        customization."""
        column_names=set([])
        for result in result_set.itervalues():
            column_names|=result.columns()
        # Create a writer
        column_names=['pmid'] + [x for x in column_names]
        output_writer=DictWriter(self._output_file, 
                                 fieldnames=column_names)
        # Add the colnames to the csv
        output_writer.writer.writerow(column_names) 
        for pmid, result in result_set.iteritems():
            outdict=result.as_dict()
            # Convert the PMID to string, which will be harmless of it's any
            # datatype but force it to display just the actual number if it's
            # a Pmid()
            outdict['pmid']=str(pmid)
            output_writer.writerow(outdict)
        return
    def output_metadata(self):
        """Exports a sidecar file (with the creative extension .metadata) that
        describes the evaluation. Override for easy customization."""
        metadata_filename=self._output_file.name + '.metadata'
        data=[]
        for potential_var, potential_var_value in self.__dict__.iteritems():
            if potential_var[0]=='_' and potential_var[1]!='_':
                data.append('%s=%r' % (potential_var[1:],
                                       potential_var_value))
        meta_out=open(metadata_filename, 'w')
        meta_out.write("[MEDRank_metadata]\n")
        meta_out.write('\n'.join(data))
        meta_out.close()
    def convert(self, terms_to_convert):
        """Override for easy customization"""
        return self._umls_converter.convert(terms_to_convert)
    def graph_article(self, article):
        if self._graph_builder is None:
            return None
        return self._graph_builder.create_graph(article)
    def graph_and_rank(self, article):
        """Turn the article into a graph, then a link matrix, and then rank
        it. Returns the ranked list of nodes."""
        article_graph=self.graph_article(article)
        article_matrix=article_graph.as_mapped_link_matrix()
        if len(article_matrix)==0:
            logging.info("Skipping article %r. It has an empty matrix.", 
                         article)
            raise CouldNotRank("Article %r is not rankable." % article)
        try:
            ranked_article=self._ranker.evaluate(article_matrix)
        except ValueError:
            logging.info("%r returned an exception while ranking %r. "
                         "Skipping.", self._ranker, article)
            raise CouldNotRank("There was an exception while ranking %r." %
                                article)
        return ranked_article
    def flatten_generated_terms(self, gold_standard_terms, generated_terms):
        """Flatten without any further preprocessing - this may be desirable 
        if, for example, all terms after the pagerank cutoff should be 
        considered equivalent. This may not always be the case."""
        return generated_terms.as_ExpressionList().flatten()
    def perform_evaluation(self, article,
                           evaluator, flat_medline, flattened_terms):
        results=evaluator.evaluate(flat_medline, flattened_terms)
        # Get the size of the LinkMatrix - we'll have to build the graph again
        # but only if we have something to build with.
        article_graph=self.graph_article(article)
        if article_graph is not None:
            results.update(article_graph.compute_measures())
        if self._graph_builder is not None:
            results.update(self._graph_builder.measurements)
        return results
    def include_article(self, article):
        """Should this article be included in the sample? Return a boolean
        specifying so. Override to customize."""
        return True
    def compute_total_recall(self, flat_gold_standard, converted_terms):
        """Computes the Total Recall of an article."""
        flat_converted=converted_terms.as_ExpressionList().flatten()
        tr=TotalRecall().evaluate(flat_gold_standard, flat_converted)
        return tr
    def run(self):
        """Perform the evaluation"""
        logging.info("Starting workflow %r run", self)
        all_results={}
        evaluator=self.create_evaluator()
        count=0
        for each_article in self._reader:
            count+=1
            logging.info("Working on article %d: %r", count, each_article)
            if not self.include_article(each_article):
                logging.log(ULTRADEBUG, "Skipping article %r due to exclusion "
                              " criteria.", each_article)
                continue
            try:
                ranked_article=self.graph_and_rank(each_article)
            except CouldNotRank:
                continue
            converted_terms=self.convert(ranked_article)
            cut_terms=converted_terms.terms_higher_than_or_equal_to(
                                self._ranking_cutoff)
            logging.debug("Lowest-ranking term is term #%d out of %d"
                          " (score=%1.5f, highest score=%1.5f)",
                          len(cut_terms), len(converted_terms),
                          [x[1] for x in cut_terms][-1],
                          [x[1] for x in cut_terms][0])
            medline_record_mesh_terms=ExpressionList().from_medline(
                    each_article.set_id.article_record().mesh_headings)
            flat_medline=medline_record_mesh_terms.flatten()
            flattened_terms=self.flatten_generated_terms(flat_medline,
                            cut_terms)
            flattened_terms=self.limit_length(flat_medline, flattened_terms)
            if len(flat_medline)==0:
                logging.warn("No gold standard available for article %r. "
                             "Omitting it from the result set.", each_article)
                continue
            eval_result=self.perform_evaluation(each_article,
                                                evaluator,
                                                flat_medline,
                                                flattened_terms)
            flattened_major_headings=\
                medline_record_mesh_terms.major_headings()
            logging.debug("Original headings: %r Major headings: %r", 
                            medline_record_mesh_terms,
                            flattened_major_headings)
            mh_result_temp=self.perform_evaluation(each_article, evaluator,
                                                   flattened_major_headings,
                                                   flattened_terms)
            mh_result=NamedResultSet("mh_", mh_result_temp)
            # Compute the total recall, too
            total_recall=self.compute_total_recall(flat_medline, 
                                                   converted_terms)
            eval_result.add(total_recall)
            # Unify the result sets
            all_results[each_article.set_id]=eval_result | mh_result
        logging.info("Writing out results.")
        self.output(all_results)
        self.output_metadata()
        return
