#!/usr/bin/env python
# encoding: utf-8
"""
graph.py

Represents a link-node weighted graph, and supports applying ranking algorithms
to it.

Created by Jorge Herskovic on 2008-05-15.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

from MEDRank.utility.logger import logging, ULTRADEBUG
import operator
import traceback
from MEDRank.computation.link import AdirectionalLink
from MEDRank.computation.link import Link
from MEDRank.computation.mapped_link_matrix import MappedLinkMatrix
from MEDRank.computation.node import Node
from MEDRank.evaluation.result import Result
from MEDRank.evaluation.result_set import ResultSet
from MEDRank.computation.distance_matrix import DistanceMatrix
from MEDRank.utility.output import HTMLEncode
import networkx as nx

# Disable warnings about spaces before and after operators (they drive me crazy)
# pylint: disable-msg=C0322, C0323

# Disable an erroneous error thrown by pylint on Graph.as_mapped_link_matrix 
# pylint: disable-msg=E1101
class GraphMeasure(Result):
    """Represents a graph measurement"""
    pass

class GraphNumberNodes(GraphMeasure):
    """Represents the number of nodes in a graph"""
    pass

class GraphNumberLinks(GraphMeasure):
    """Represents the number of links in the graph."""
    pass
    
class GraphLinkDegree(GraphMeasure):
    """Represents the average number of links per node"""
    pass

class GraphAverageNodeWeight(GraphMeasure):
    """Represents the average weight of the nodes in the graph"""
    pass

class GraphAverageLinkWeight(GraphMeasure):
    """Represents the average weight of the links in the graph"""
    pass
    
class GraphRelativeOutCentrality(GraphMeasure):
    """Represents the average Relative OutCentrality of the nodes."""
    pass

class GraphRelativeInCentrality(GraphMeasure):
    """Represents the average relative in-centrality of the nodes."""
    pass

class GraphCompactness(GraphMeasure):
    """Represents the Compactness measure of the graph."""
    pass

class GraphStratum(GraphMeasure):
    """Represents the Stratum of the graph"""
    pass
    
class Graph(nx.DiGraph):
    """Extends a NetworkX graph with MEDRank-specific functionality."""
    def __init__(self):
        nx.DiGraph.__init__(self)
        # self._entities=set([])

    # @staticmethod
    # def entity_collision_handler(already_in_set, newcomer):
        # """Default entity collision handler. Override to implement custom
        # behavior.
        # Reasonable operations would be adding the weights, choosing the
        # largest, etc.
        # The default collision_handler ignores the newcomer.
        # Beware of changing this collision handler, as add_relationship
        # ALWAYS tries to add every entity to the graph."""
        # return already_in_set
    # def add_entity(self, new_entity, collision_handler=None):
        # """Takes an entity and adds it to the set of entities."""
        # if new_entity in self._entities:
            # old_entity=(self._entities & set([new_entity])).pop()
            # self._entities.remove(old_entity)
            # new_entity=self.entity_collision_handler(old_entity,
            #                                          new_entity)
        # self._entities.add(new_entity)

    def add_relationship(self, relationship):
        """Takes a Link and adds it to the set of relationships. This is just
        an intermediate step; consolidate_graph should be called before
        actually using the graph for anything.
        """
        self.add_edge(relationship.node1, relationship.node2)
        self[relationship.node1][relationship.node2]['MRLink'] = relationship
        self[relationship.node1][relationship.node2]['weight'] = relationship.weight
        # This is to support old-style MEDRank graphs. 
        # Honestly, this breaks all rules of object-oriented design. Sorry!
        if isinstance(relationship, AdirectionalLink):
            self.add_edge(relationship.node2, relationship.node1)
            self[relationship.node2][relationship.node1]['MRLink'] = relationship
            self[relationship.node2][relationship.node1]['weight'] = relationship.weight
    # The relationships property.
    def relationships_fget(self):
        "Getter for the relationships property."
        # Return a defensive copy
        return [self[x[0]][x[1]]['MRLink'] for x in self.edges()]
    relationships = property(relationships_fget)
    def nodes_fget(self):
        """Returns a node_id->node dictionary containing the same nodes as the actual
        graph."""
        result = {}
        for r in nx.Graph.nodes(self):
            result[r.node_id] = r
        return result
    nodes = property(nodes_fget)
    def consolidate_graph(self):
        """NOP - nx does not require it."""
        return
    def __repr__(self):
        return "<Graph: %r>" % self._relationships
    def __str__(self):
        """Pretty-printing method"""
        return "\t" + '\n\t'.join([str(x) for x in self._relationships]) 
    def _consolidate_if_necessary(self):
        """Consolidates the graph if it's necessary, ignores the call 
        otherwise"""
        return
    def as_mapped_link_matrix(self):
        """Turns a graph into a MappedLinkMatrix"""
        # Build a set of all the known nodes
        logging.log(ULTRADEBUG, "Transforming Graph %r into a MappedLinkMatrix",
                    self)
        nodes = set([x.node1 for x in self.relationships])
        nodes |= set([x.node2 for x in self.relationships])
        # Create a MappedLinkMatrix with these as terms
        nodes = list(nodes)
        new_matrix = MappedLinkMatrix(
                        nx.convert.to_numpy_matrix(self, nodes).view(MappedLinkMatrix))
        new_matrix.terms = nodes
        return new_matrix
    def compute_measures(self):
        """Computes graph metrics for the current object."""
        # TODO: Replace with nx measures 
        logging.log(ULTRADEBUG, "Computing graph metrics for %r", self)
        graph_measures = ResultSet()
        graph_measures.add(GraphNumberLinks(len(self._relationships)))
        unique_nodes = set()
        for a_relation in self._relationships:
            unique_nodes.add(a_relation.node1)
            unique_nodes.add(a_relation.node2)
        graph_measures.add(GraphNumberNodes(len(unique_nodes)))
        graph_measures.add(GraphAverageNodeWeight(reduce(operator.add,
                                    [x.weight for x in unique_nodes]) / 
                                    float(len(unique_nodes))))
        graph_measures.add(GraphAverageLinkWeight(reduce(operator.add,
                                    [x.weight for x in self._relationships]) / 
                                    float(len(self._relationships))))
        graph_measures.add(GraphLinkDegree(float(len(self._relationships)) / 
                                           float(len(unique_nodes))))
        logging.log(ULTRADEBUG, "Starting computation of the distance matrix.")
        distmat = DistanceMatrix(self)
        logging.log(ULTRADEBUG, "Distance matrix obtained. Computing stats.")
        rocs = [distmat.relative_out_centrality(x) for x in 
              xrange(len(distmat))]
        rics = [distmat.relative_in_centrality(x) for x in 
              xrange(len(distmat))]
        avrocs = reduce(operator.add, rocs) / float(len(distmat))
        avrics = reduce(operator.add, rics) / float(len(distmat))
        graph_measures.add(GraphRelativeOutCentrality(avrocs))
        graph_measures.add(GraphRelativeInCentrality(avrics))
        graph_measures.add(GraphStratum(distmat.stratum()))
        graph_measures.add(GraphCompactness(distmat.compactness()))
        logging.log(ULTRADEBUG, "Finished computing graph metrics.")
        return graph_measures
    def as_ncol_file(self):
        """Builds an .ncol file for use in LGL (the Large Graph Layout 
        tool)"""
        replacements = ' -[]{}()*&^%$#@()/?!\\|=+"\';:,.<>'
        def clean(a_string, to_eliminate=replacements):
            "Eliminate unwanted characters from a string. LGL is picky."
            new_string = a_string
            for each_one_to_eliminate in to_eliminate:
                new_string = new_string.replace(each_one_to_eliminate, '_')
            return new_string
        self._consolidate_if_necessary()
        output = []
        for a_relation in self.relationships:
            node1 = clean(a_relation.node1.name)
            node2 = clean(a_relation.node2.name)
            if node1 == node2: 
                continue # Skip edges from a node to itself; LGL can't handle them.
            output.append("%s %s %1.7f" % (node1, node2,
                                           a_relation.weight))
        return '\n'.join(output)
    def as_neato_file(self):
        """Builds a neato file for use with GraphViz"""
        replacements = ' -[]{}()*&^%$#@()/?!\\|=+"\';:,.<>'
        def clean(a_string, to_eliminate=replacements):
            "Eliminate unwanted characters from a string. LGL is picky."
            new_string = a_string
            for each_one_to_eliminate in to_eliminate:
                new_string = new_string.replace(each_one_to_eliminate, '_')
            return new_string
        self._consolidate_if_necessary()
        output = ["graph G {"]
        for a_relation in self.relationships:
            node1 = clean(a_relation.node1.name)
            node2 = clean(a_relation.node2.name)
            if node1 == node2 or a_relation.weight == 0: 
                continue # Skip edges from a node to itself and 0-weight edges 
            output.append("%s -- %s [weight=%1.2f];" % (node1, node2, a_relation.weight))
        output.append("}")
        return '\n'.join(output)
    def as_graphml_file(self):
        graph = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
        <graphml xmlns="http://graphml.graphdrawing.org/xmlns" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:y="http://www.yworks.com/xml/graphml" xmlns:yed="http://www.yworks.com/xml/yed/3" xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns http://www.yworks.com/xml/schema/graphml/1.1/ygraphml.xsd">
        <key for="graphml" id="d0" yfiles.type="resources"/>
        <key for="node" id="d1" yfiles.type="nodegraphics" />
        <key for="edge" id="d2" yfiles.type="edgegraphics" />
        <key for="node" id="node_id" attr.name="MR_id" attr.type="string" />
        <key for="edge" id="edge_id" attr.name="MR_id" attr.type="string" />
        <key for="edge" id="edge_lbl" attr.name="description" attr.type="string" />
        <key for="node" id="node_lbl" attr.name="description" attr.type="string" />        
        <key id="ew" for="edge" attr.name="weight" attr.type="double" />
        <graph edgedefault="directed" id="G">
        %(nodes)s
        %(edges)s
        </graph>
        <data key="d0">
          <y:Resources/>
        </data>
        </graphml>
        """

        node = """<node id="%(nodeid)s">
            <data key="d1">
                <y:ShapeNode>
                   <y:NodeLabel>%(label)s</y:NodeLabel>
                   <y:Shape type="ellipse" />
                </y:ShapeNode>
            </data>
            <data key="node_id">%(nodeid)s</data>
            <data key="node_lbl">%(label)s</data>
        </node>"""

        edge = """<edge id="%(name)s" source="%(src)s" target="%(tgt)s">
             <data key="d2">
                <y:PolyLineEdge>
                  <y:Arrows source="none" target="standard"/>
                  <y:EdgeLabel>%(label)s</y:EdgeLabel>
                </y:PolyLineEdge>
              </data>
              <data key="ew">%(weight)f</data>
              <data key="edge_id">%(name)s</data>
              <data key="edge_lbl">%(label)s</data>
            </edge>"""
        nodes = {}
        edges = []
        n = 0
        e = 0

        for l in self.relationships:
            n1, rel, n2 = l.node1, l.name, l.node2
            if n1 not in nodes:
                nodes[n1] = n
                n = n + 1
            if n2 not in nodes:
                nodes[n2] = n
                n = n + 1
            edges.append(edge % {"name":  "e%d" % e,
                                 "src":   "%s" % n1.node_id,
                                 "tgt":   "%s" % n2.node_id,
                                 "weight": l.weight,
                                 "label": "" if rel is None else HTMLEncode(rel)})
            e = e + 1
        nodelist = []
        for nn in nodes:
            nodelist.append(node % {"nodeid":  "%s" % nn.node_id,
                                 "label": "" if nn.name is None else HTMLEncode(nn.name)})

        return graph % {
                        "nodes": '\n'.join(nodelist),
                        "edges": '\n'.join(edges)
                    }
    def from_graphml_file(self, file_object, default_link=Link):
        from xml.etree.ElementTree import iterparse
        def get_subelement_data(elem, key):
            result = [x.text for x in elem.getiterator()
                    if x.tag == "{http://graphml.graphdrawing.org/xmlns}data"
                    and x.get('key') == key]
            if len(result) == 0:
                return None
            return result[0]
        nodes = {}
        # Discover the names of the attributes we're looking for by investigating the keys
        # Then actually read the file
        keystore = {}
        for event, element in iterparse(file_object):
            #print element
            if element.tag == "{http://graphml.graphdrawing.org/xmlns}key":
                if element.get('attr.name') is None:
                    continue
                keystore[element.get('for') + '.' + element.get('attr.name')] = element.get('id')
            # print keystore
            if element.tag == "{http://graphml.graphdrawing.org/xmlns}node":
                # The next line supports yEd's NodeLabel and Profuse's label
                nodename = get_subelement_data(element, keystore['node.description'])
                if nodename is None:
                    nodename = "NoName"
                nodekey = get_subelement_data(element, keystore['node.MR_id'])
                nodes[element.get('id')] = Node(nodekey, nodename, 1.0)
            if element.tag == "{http://graphml.graphdrawing.org/xmlns}edge":
                n1 = nodes[element.get('source')]
                n2 = nodes[element.get('target')]
                try:
                    weight = float(get_subelement_data(element, keystore['edge.weight']))
                except:
                    logging.warn('Failed at reading weight because of:\n%s',
                                 traceback.format_exc())
                    weight = 1.0
                try:
                    relname = get_subelement_data(element, keystore['edge.description'])
                except:
                    relname = ""
                self.add_relationship(default_link(n1, n2, weight, relname))
        self.consolidate_graph()
        return
    def as_networkx_graph(self):
        return self
