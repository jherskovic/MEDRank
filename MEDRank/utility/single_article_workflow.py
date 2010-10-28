#!/usr/bin/env python
# encoding: utf-8
"""
single_article_workflow.py

Created by Jorge Herskovic on 2010-06-29.
Copyright (c) 2010 University of Texas - Houston. All rights reserved.
"""

import copy
from MEDRank.utility.single_item_workflow import SingleItemWorkflow
from MEDRank.utility.logger import logging, ULTRADEBUG
from MEDRank.evaluation.savcc_normalized_matrix import SavccNormalizedMatrix
from MEDRank.mesh.tree import Tree
from MEDRank.evaluation.common import comprehensive
from MEDRank.evaluation.recall import TotalRecall
from MEDRank.mesh.expression import ExpressionList
from MEDRank.umls.converter import Converter
from MEDRank.umls.ranked_converter import RankedConverter
from MEDRank.evaluation.named_result_set import NamedResultSet
from MEDRank.utility.workflow import CouldNotRank

#import time
# Disable warnings about spaces before operators (they drive me crazy)
# pylint: disable-msg=C0322

class SingleArticleWorkflow(SingleItemWorkflow):
    """Contains a basic workflow through the system for a single article.
    The parameters are:
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
    Call the process() method to execute it."""
    def __init__(self, graph_builder_constructor, graph_builder_params,
                 ranker_constructor, ranker_params,
                 eval_parameters, 
                 ranking_cutoff,
                 mesh_tree_filename, distance_matrix_filename,
                 distance_function,
                 umls_converter_data_filename):
        logging.debug("Setting up a SingleArticleWorkflow instance.")
        SingleItemWorkflow.__init__(self, graph_builder_constructor,
                                    graph_builder_params, ranker_constructor,
                                    ranker_params, ranking_cutoff)
        if mesh_tree_filename is not None:
            logging.debug("Creating a Tree instance from %s", mesh_tree_filename)
            self._mesh_tree=Tree(mesh_tree_filename)
        else:
            self._mesh_tree=None
        if distance_matrix_filename is not None:
            logging.debug("Creating SAVCC distance matrix with %r and distance "
                          "function %r", 
                          distance_matrix_filename, distance_function)
            self._matrix=SavccNormalizedMatrix(
                        open(distance_matrix_filename, "rb"), distance_function)
        else:
            self._matrix=None
        logging.debug("Filling in the rest of the evaluation parameters.")
        self._eval_parameters=copy.deepcopy(eval_parameters)
        self._eval_parameters.mesh_tree=self._mesh_tree
        self._eval_parameters.savcc_matrix=self._matrix
        logging.debug("My evaluation parameters are: %r", 
                      self._eval_parameters)
        if umls_converter_data_filename is None:
            converter_data=None
        else:
            converter_data=pickle.load(open(umls_converter_data_filename, 
                                            "rb"))
        self._umls_converter=self.create_converter(self._mesh_tree, 
                                                   converter_data)
        logging.debug("My converter is: %r", self._umls_converter)

        self.evaluator=self.create_evaluator()
        return
    def limit_length(self, gold_standard_terms, generated_terms):
        """Limits the length of the generated terms and returns the new list.
        By default it just truncates the list to the length of the gold 
        standard. Override to customize."""
        return generated_terms[:len(gold_standard_terms)]
    def create_evaluator(self):
        """Creates and returns the evaluator we'll use - override for easy
        customization"""
        return comprehensive(self._eval_parameters)
    def create_converter(self, mesh_tree, converter_data):
        """Creates and returns the UMLS converter we'll use - override for easy
        customization"""
        return RankedConverter(Converter(mesh_tree, converter_data))
    def convert(self, terms_to_convert):
        """Override for easy customization"""
        return self._umls_converter.convert(terms_to_convert)
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
        article_graph=self.graph_item(article)
        if article_graph is not None:
            results.update(article_graph.compute_measures())
        if self._graph_builder is not None:
            results.update(self._graph_builder.measurements)
        return results
    def include_article(self, article):
        """Should this article be included in the sample? Return a boolean
        specifying so. Override to customize."""
        return self.include_item(article)
    def compute_total_recall(self, flat_gold_standard, converted_terms):
        """Computes the Total Recall of an article."""
        flat_converted=converted_terms.as_ExpressionList().flatten()
        tr=TotalRecall().evaluate(flat_gold_standard, flat_converted)
        return tr
    def process_article(self, each_article):
        if not self.include_article(each_article):
            logging.log(ULTRADEBUG, "Skipping article %r due to exclusion "
                          " criteria.", each_article)
            return
        try:
            ranked_article=self.graph_and_rank(each_article)
        except CouldNotRank:
            return
        logging.debug("Ranked article: %r", ranked_article)
        converted_terms=self.convert(ranked_article)
        logging.debug("Converted terms: %r", converted_terms)
        cut_terms=converted_terms.terms_higher_than_or_equal_to(
                            self._ranking_cutoff)
        logging.debug("Cut terms: %r", cut_terms)
        try:
            medline_record_mesh_terms=ExpressionList().from_medline(
                    each_article.set_id.article_record()['MH'])
        except:
            logging.warn("Could not obtain an article record for %r. "
                         "Skipping.", each_article)
            return
        flat_medline=medline_record_mesh_terms.flatten()
        flattened_terms=self.flatten_generated_terms(flat_medline,
                        cut_terms)
        flattened_terms=self.limit_length(flat_medline, flattened_terms)
        if len(flat_medline)==0:
            logging.warn("No gold standard available for article %r. "
                         "Omitting it from the result set.", each_article)
            return
        eval_result=self.perform_evaluation(each_article,
                                            self.evaluator,
                                            flat_medline,
                                            flattened_terms)
        flattened_major_headings=\
            medline_record_mesh_terms.major_headings()
        #logging.debug("Original headings: %r Major headings: %r", 
        #                medline_record_mesh_terms,
        #                flattened_major_headings)
        logging.debug("Flattened MeSH terms: %r", flat_medline)
        logging.debug("Flattened generated terms: %r", flattened_terms)
        mh_result_temp=self.perform_evaluation(each_article, self.evaluator,
                                               flattened_major_headings,
                                               flattened_terms)
        mh_result=NamedResultSet("major_", mh_result_temp)
        # Compute the total recall, too
        total_recall=self.compute_total_recall(flat_medline, 
                                               converted_terms)
        eval_result.add(total_recall)
        # Unify the result sets
        self.all_results[each_article.set_id]=eval_result | mh_result
        return

