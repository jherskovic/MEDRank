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
    
class Graph(object):
    """Describes a link-node graph. In these graphs, there can be only one
    instance of a node and only one link between pairs of nodes. This second
    restriction is to force explicit resolution of the issue of multiple
    links, instead of making assumptions."""
    def __init__(self):
        self._relationships=set([])
        self._temp_relationships={}
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
                                                     # new_entity)
        # self._entities.add(new_entity)

    @staticmethod    
    def relationship_collision_handler(list_of_relationships):
        """Default relationship collision handler. Override to implement
        custom behavior.
        relationship_collision_handler will be called for each set of
        matching relationships. It should take a list of relationships and
        return just one.
        Reasonable operations would be adding the weights, choosing the
        largest, etc.
        The default collision_handler returns the strongest relationship."""
        # Use the D-S-U pattern
        sorted_relationships=[(x.weight, x) for x in list_of_relationships]
        sorted_relationships.sort(reverse=True)
        return sorted_relationships[0][1]
    def add_relationship(self, relationship):
        """Takes a Link and adds it to the set of relationships. This is just
        an intermediate step; consolidate_graph should be called before
        actually using the graph for anything.
        """
        relhash=hash(relationship)
        if relhash in self._temp_relationships:
            self._temp_relationships[relhash].append(relationship)
        else:
            self._temp_relationships[relhash]=[relationship]
    # The relationships property.
    def relationships_fget(self):
        "Getter for the relationships property."
        # Return a defensive copy
        return [x for x in self._relationships]
    relationships=property(relationships_fget)
    def nodes_fget(self):
        """Returns a node_id->node dictionary containing the same nodes as the actual
        graph."""
        result={}
        for r in self._relationships:
            n1, n2=r.node1, r.node2
            if n1.node_id not in result:
                result[n1.node_id]=n1
            if n2.node_id not in result:
                result[n2.node_id]=n2
        return result
    nodes=property(nodes_fget)
    def consolidate_graph(self):
        """Turns the relationships stored temporarily into an actual graph.
        collision_handler specifies a callback that will be called if the 
        relationship is already in the set. The prototype should be:
        def collision_handler(already_in_set, candidate):
            return just_the_link_that_should_be_in_the_set
        Reasonable operations would be adding the weights, choosing the
        largest, etc.
        The default collision_handler ignores the newcomer."""
        
        for relset in self._temp_relationships.itervalues():
            # We will keep just one relationship from each set with the same
            # hash, by using relationship_collision_handler to reduce the 
            # list. When the list has a single element reduce() doesn't call
            # the handler function, which makes it perfect for our purposes.
            self._relationships.add(self.relationship_collision_handler(
                                        relset))
        self._temp_relationships={} # Delete the tempset
        # Consolidate nodes by node_id, so there will only be one unique node 
        # object per node_id in the graph.
        canonical_nodes=self.nodes
        for r in self._relationships:
            n1, n2=r.node1, r.node2
            r.node1=canonical_nodes[n1.node_id]
            r.node2=canonical_nodes[n2.node_id]
        
    def __repr__(self):
        return "<Graph: %r>" % self._relationships
    def __str__(self):
        """Pretty-printing method"""
        return "\t" + '\n\t'.join([str(x) for x in self._relationships]) 
    def _consolidate_if_necessary(self):
        """Consolidates the graph if it's necessary, ignores the call 
        otherwise"""
        if len(self._temp_relationships)>0:
            logging.debug("The graph needs to be consolidated. There are "
                          "relationships in temp storage. Consolidating now.")
            self.consolidate_graph()
    def as_mapped_link_matrix(self):
        """Turns a graph into a MappedLinkMatrix"""
        self._consolidate_if_necessary()
        # Build a set of all the known nodes
        logging.log(ULTRADEBUG, "Transforming Graph %r into a MappedLinkMatrix",
                    self)
        nodes=set([x.node1 for x in self._relationships])
        nodes|=set([x.node2 for x in self._relationships])
        # Create a MappedLinkMatrix with these as terms
        new_matrix=MappedLinkMatrix(nodes)
        # Iterates through the relationships, adding each one to the 
        # MappedLinkMatrix 
        for a_relation in self._relationships:
            from_coordinate=new_matrix.get_term_position(a_relation.node1)
            to_coordinate=new_matrix.get_term_position(a_relation.node2)
            # If the relation is adirectional, we must add it in both
            # from->to and to->from positions
            new_matrix[from_coordinate, to_coordinate]=a_relation.weight
            if isinstance(a_relation, AdirectionalLink):
                new_matrix[to_coordinate, from_coordinate]=a_relation.weight
                
        logging.log(ULTRADEBUG, "MappedLinkMatrix %r built", new_matrix)
        return new_matrix
    def compute_measures(self):
        """Computes graph metrics for the current object."""
        self._consolidate_if_necessary()
        logging.log(ULTRADEBUG, "Computing graph metrics for %r", self)
        graph_measures=ResultSet()
        graph_measures.add(GraphNumberLinks(len(self._relationships)))
        unique_nodes=set()
        for a_relation in self._relationships:
            unique_nodes.add(a_relation.node1)
            unique_nodes.add(a_relation.node2)
        graph_measures.add(GraphNumberNodes(len(unique_nodes)))
        graph_measures.add(GraphAverageNodeWeight(reduce(operator.add,
                                    [x.weight for x in unique_nodes])/
                                    float(len(unique_nodes))))
        graph_measures.add(GraphAverageLinkWeight(reduce(operator.add,
                                    [x.weight for x in self._relationships])/
                                    float(len(self._relationships))))
        graph_measures.add(GraphLinkDegree(float(len(self._relationships))/
                                           float(len(unique_nodes))))
        logging.log(ULTRADEBUG, "Starting computation of the distance matrix.")
        distmat=DistanceMatrix(self.as_mapped_link_matrix())
        logging.log(ULTRADEBUG, "Distance matrix obtained. Computing stats.")
        rocs=[distmat.relative_out_centrality(x) for x in 
              xrange(len(distmat))]
        rics=[distmat.relative_in_centrality(x) for x in 
              xrange(len(distmat))]
        avrocs=reduce(operator.add, rocs)/float(len(distmat))
        avrics=reduce(operator.add, rics)/float(len(distmat))
        graph_measures.add(GraphRelativeOutCentrality(avrocs))
        graph_measures.add(GraphRelativeInCentrality(avrics))
        graph_measures.add(GraphStratum(distmat.stratum()))
        graph_measures.add(GraphCompactness(distmat.compactness()))
        logging.log(ULTRADEBUG, "Finished computing graph metrics.")
        return graph_measures
    def as_ncol_file(self):
        """Builds an .ncol file for use in LGL (the Large Graph Layout 
        tool)"""
        replacements=' -[]{}()*&^%$#@()/?!\\|=+"\';:,.<>'
        def clean(a_string, to_eliminate=replacements):
            "Eliminate unwanted characters from a string. LGL is picky."
            new_string=a_string
            for each_one_to_eliminate in to_eliminate:
                new_string=new_string.replace(each_one_to_eliminate, '_')
            return new_string
        self._consolidate_if_necessary()
        output=[]
        for a_relation in self.relationships:
            node1=clean(a_relation.node1.name)
            node2=clean(a_relation.node2.name)
            if node1==node2: 
                continue # Skip edges from a node to itself; 
                         # LGL can't handle them.
            output.append("%s %s %1.7f" % (node1, node2,
                                           a_relation.weight))
        return '\n'.join(output)
    def as_neato_file(self):
        """Builds a neato file for use with GraphViz"""
        replacements=' -[]{}()*&^%$#@()/?!\\|=+"\';:,.<>'
        def clean(a_string, to_eliminate=replacements):
            "Eliminate unwanted characters from a string. LGL is picky."
            new_string=a_string
            for each_one_to_eliminate in to_eliminate:
                new_string=new_string.replace(each_one_to_eliminate, '_')
            return new_string
        self._consolidate_if_necessary()
        output=["graph G {"]
        for a_relation in self.relationships:
            node1=clean(a_relation.node1.name)
            node2=clean(a_relation.node2.name)
            if node1==node2 or a_relation.weight==0: 
                continue # Skip edges from a node to itself and 0-weight edges 
            output.append("%s -- %s [weight=%1.2f];" % (node1, node2, a_relation.weight))
        output.append("}")
        return '\n'.join(output)
    def as_graphml_file(self):
        graph="""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
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

        node="""<node id="%(nodeid)s">
            <data key="d1">
                <y:ShapeNode>
                   <y:NodeLabel>%(label)s</y:NodeLabel>
                   <y:Shape type="ellipse" />
                </y:ShapeNode>
            </data>
            <data key="node_id">%(nodeid)s</data>
            <data key="node_lbl">%(label)s</data>
        </node>"""

        edge="""<edge id="%(name)s" source="%(src)s" target="%(tgt)s">
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
        nodes={}
        edges=[]
        n=0
        e=0

        for l in self.relationships:
            n1, rel, n2=l.node1, l.name, l.node2
            if n1 not in nodes:
                nodes[n1]=n
                n=n+1
            if n2 not in nodes:
                nodes[n2]=n
                n=n+1
            edges.append(edge % {"name":  "e%d" % e,
                                 "src":   "%s" % n1.node_id,
                                 "tgt":   "%s" % n2.node_id,
                                 "weight": l.weight,
                                 "label": "" if rel is None else HTMLEncode(rel)})
            e=e+1
        nodelist=[]
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
            result=[x.text for x in elem.getiterator()
                    if x.tag=="{http://graphml.graphdrawing.org/xmlns}data"
                    and x.get('key')==key]
            if len(result)==0:
                return None
            return result[0]
        nodes={}
        # Discover the names of the attributes we're looking for by investigating the keys
        # Then actually read the file
        keystore={}
        for event, element in iterparse(file_object):
            #print element
            if element.tag=="{http://graphml.graphdrawing.org/xmlns}key":
                if element.get('attr.name') is None:
                    continue
                keystore[element.get('for')+'.'+element.get('attr.name')]=element.get('id')
            # print keystore
            if element.tag=="{http://graphml.graphdrawing.org/xmlns}node":
                # The next line supports yEd's NodeLabel and Profuse's label
                nodename=get_subelement_data(element, keystore['node.description'])
                if nodename is None:
                    nodename="NoName"
                nodekey=get_subelement_data(element, keystore['node.MR_id'])
                nodes[element.get('id')]=Node(nodekey, nodename, 1.0)
            if element.tag=="{http://graphml.graphdrawing.org/xmlns}edge":
                n1=nodes[element.get('source')]
                n2=nodes[element.get('target')]
                try:
                    weight=float(get_subelement_data(element, keystore['edge.weight']))
                except:
                    logging.warn('Failed at reading weight because of:\n%s', 
                                 traceback.format_exc())
                    weight=1.0
                try:
                    relname=get_subelement_data(element, keystore['edge.description'])
                except:
                    relname=""
                self.add_relationship(default_link(n1, n2, weight, relname))
        self.consolidate_graph()
        return
    def as_networkx_graph(self):
        import networkx as nx
        G=nx.Graph()
        G.add_weighted_edges_from([
            (l.node1.node_id, l.node2.node_id, l.weight)
            for l in self.relationships])
        return G