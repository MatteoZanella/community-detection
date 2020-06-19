import argparse
import os
from itertools import dropwhile
import graph_tool.all as gt
import numpy as np

MAX_EDGES_LIST_LEN = 10000

parser = argparse.ArgumentParser()
parser.add_argument("graph", type=str,
                    help="The .txt graph that needs to be saved as binary, one edge pair for every line")
parser.add_argument("-d", "--directed", action="store_true",
                    help="Specify if the graph is directed. By default it's undirected")
parser.add_argument("-c", "--communities", type=str,
                    help="The .txt association of communities, one community for every line")
parser.add_argument("-l", "--labels", action="store_true",
                    help="Specify if the communities are a list of association <vertex> <label>. By default each line <vertex> <vertex> ... <vertex> represent a community")
parser.add_argument("-r", "--reduce", action="store_true",
                    help="If set, vertices not belonging to a community will be deleted")
args = parser.parse_args()

# Create a new instance of the graph-
graph = gt.Graph(directed=args.directed)

# Decide the output name for files based on the basename of the input graph text file
basename = os.path.basename(args.graph)
output_name = basename[:basename.find(".")]

# Whitelist to filter out useless nodes
if args.communities is not None:
    with open(args.communities) as comm_file:
        if not args.labels:
            whitelist = set()
            for line in dropwhile(lambda l: l.startswith('#'), comm_file):
                for vertex in line.split():
                    whitelist.add(int(vertex))

# Read the graph text file and build the corresponding graph
with open(args.graph) as graph_file:
    edges_list = []
    for line in dropwhile(lambda l: l.startswith('#'), graph_file):
        edge = tuple([int(num) for num in line.split()])
        if edge[0] in whitelist and edge[1] in whitelist:
            edges_list.append(edge)
        # edges_list.append((int(num) for num in line.split()))
        if len(edges_list) >= MAX_EDGES_LIST_LEN:
            graph.add_edge_list(edges_list)
            edges_list.clear()
    graph.add_edge_list(edges_list)

if args.communities is not None:
    # Add a new internal vertex property to the graph, a vector of communities labels
    graph.vp.comm = graph.new_vp("object", vals=[set() for _ in range(graph.num_vertices())])
    # Add a new internal graph property to the graph, holding the number of communities
    graph.gp.num_comm = graph.new_gp("int")
    # Read the communities file and create the community vector
    with open(args.communities) as comm_file:
        if not args.labels:
            # When the communities file is structured as <vtx> <vtx> ... <vtx>
            # Compute internal density of every community and a list of communities
            communities = []
            internal_density = []
            v_filter = graph.new_vertex_property("boolean", val=False)
            for community, line in enumerate(dropwhile(lambda l: l.startswith('#'), comm_file)):
                communities.append({int(node) for node in line.split()})
                # Compute internal degree
                for v in communities[community]:
                    v_filter[graph.vertex(v)] = True
                graph.set_vertex_filter(v_filter)
                internal_degree = np.sum(graph.get_total_degrees(list(communities[community])))
                for v in communities[community]:
                    v_filter[graph.vertex(v)] = False
                graph.clear_filters()
                # Compute internal density
                n_vertices = len(communities[community])
                density = internal_degree / (n_vertices * (n_vertices - 1))
                internal_density.append(density)
            # Delete the bottom quartile
            threshold = np.quantile(np.array(internal_density), 0.25, interpolation='midpoint')
            f_communities = [comm for (density, comm) in zip(internal_density, communities) if density > threshold]
            # Insert the communities to the graph
            for community, vertices in enumerate(f_communities):
                for vtx in vertices:
                    graph.vp.comm[graph.vertex(vtx)].add(community)
            # Add the number of communities
            graph.gp.num_comm = len(f_communities)
        else:
            # When the communities file is structured as <vertex> <label>
            # Translation dict for normalizing the community index
            translate = {}
            num_comm = 0
            for line in dropwhile(lambda l: l.startswith('#'), comm_file):
                node, community = (int(num) for num in line.split())
                if community not in translate:
                    translate[community] = num_comm
                    num_comm += 1
                graph.vp.comm[graph.vertex(node)].add(translate[community])
            graph.gp.num_comm = num_comm

# Optionally delete nodes not belonging to any community
if args.reduce:
    unassigned_vertices = [v for v in graph.get_vertices() if not graph.vp.comm[v]]
    graph.remove_vertex(unassigned_vertices, fast=True)

# Cleanup: removing all vertices that aren't connected with any other vertex mainly because of gaps in the vertex count
single_vertices = np.where(graph.get_total_degrees(graph.get_vertices()) == 0)[0]
graph.remove_vertex(single_vertices, fast=True)

print(f"Graph is directed: {graph.is_directed()}")
print(f"Found [{graph.num_vertices()}] vertices and [{graph.num_edges()}] edges")
print(f"Found [{graph.gp.num_comm}] communities!")
print("==== Communities saved in g.vp.comm and their size saved in g.gp.num_comm ====")
# Save the graph as binary
graph.save(f"{output_name}.gt")
