import graph_tool.all as gt
import numpy as np


def filter_unassigned_v(g: gt.Graph):
    prop = g.new_vp("bool")
    prop.a = np.array([len(g.vp.comm[v]) > 0 for v in g.vertices()])
    g.set_vertex_filter(prop)


def normalize(comm: gt.VertexPropertyMap):
    translate = {}
    num_comm = 0
    for v in comm.get_graph().get_vertices():
        translated_comm = set()
        for community in comm[v]:
            if community not in translate:
                translate[community] = num_comm
                num_comm += 1
            translated_comm.add(translate[community])
        comm[v] = translated_comm
    return num_comm
