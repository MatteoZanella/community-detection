import math
import numpy as np
import graph_tool.all as gt


def comm_membership(c: gt.VertexPropertyMap):
    graph = c.get_graph()
    o_n = 0 # number of nodes with more than 1 community
    o_min = math.inf
    o_max = 0
    o_mean = 0
    for v in graph.get_vertices():
        o_mean += len(c[v]) / graph.num_vertices()
        o_min = o_min if o_min < len(c[v]) else len(c[v])
        o_max = o_max if o_max > len(c[v]) else len(c[v])
        if len(c[v]) > 1:
            o_n += 1
    return o_min, o_max, o_mean, o_n

def comm_size(c: gt.VertexPropertyMap, num_comm: int):
    graph = c.get_graph()
    c_min = math.inf
    c_max = 0
    c_mean = 0
    sizes = np.zeros(num_comm, dtype='int')
    for v in graph.get_vertices():
        for label in c[v]:
            sizes[label] += 1
    for c_size in sizes:
        c_min = c_min if c_min < c_size else c_size
        c_max = c_max if c_max > c_size else c_size
        c_mean += c_size / num_comm
    return c_min, c_max, c_mean
