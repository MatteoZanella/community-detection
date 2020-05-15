import graph_tool.all as gt
import numpy as np


def filter_unassigned_v(g: gt.Graph):
    prop = g.new_vp("bool")
    prop.a = np.array([len(g.vp.comm[v]) > 0 for v in g.vertices()])
    g.set_vertex_filter(prop)
