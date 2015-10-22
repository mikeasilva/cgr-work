# -*- coding: utf-8 -*-
"""
Generalized Graph Creating Script
Created on Thu Oct 22 11:31:10 2015

@author: Michael Silva
"""

"""
In order to work this script requires two csv files.

Filename: nodes.csv
Description: The unique id and the name of the node.
Example:

+====+===========+
| Id | Node Name |
+====+===========+
| 0  | Node A    |
|        ...     |
| n  | Node B    |
+====+===========+

Filename: edges.csv
Description: The ids of the nodes the edges are connected to.  The weight is optional.
Example:
+========+========+=========+
| Source | Target | Weight  |
+========+========+=========+
| 0      | n      | 1000000 |
+========+========+=========+
"""
# Libraries needed for the script
import pandas as pd
import networkx as nx

# Is this a directional graph?
is_directional_graph = False

# Read in data
edges = pd.read_csv('edges.csv')
nodes = pd.read_csv('nodes.csv')

# Create the graph
if is_directional_graph:
    G = nx.DiGraph()
else:
    G = nx.Graph()

# Add in the edges
for row in edges.iterrows():
	# Use this if no weight is defined
    G.add_edge(row[1].Source, row[1].Target)
	# If weight is defined comment out the line above and uncomment the next line
	# G.add_edge(row[1].Source, row[1].Target, weight=row[1].Weight)

# Add the node attributes
labels = nodes[['Node Name']].to_dict()
labels = labels['Node Name']
nx.set_node_attributes(G, 'label', labels)

# Write the graph to files
nx.write_graphml(G,'Graph.graphml')