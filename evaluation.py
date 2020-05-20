import math
import numpy as np
import graph_tool.all as gt
from itertools import combinations
import utility


def _h(w, n):
    p = float(w) / n
    return -p * math.log2(p) if p > 0 else 0


def _cover_entropy(cover: np.ndarray, num_vertices: int):
    h_cover = 0
    h_cover_i = np.empty(cover.shape)
    for i, community in enumerate(cover):
        h_cover_i[i] = _h(len(community), num_vertices) + _h(num_vertices - len(community), num_vertices)
        h_cover += h_cover_i[i]
    # Returns an array of communities' entropy and the total entropy of the cover
    return h_cover_i, h_cover


def NMI_max(c1: gt.VertexPropertyMap, num_comm_c1, c2: gt.VertexPropertyMap, num_comm_c2):
    num_vtx = c1.get_graph().num_vertices()
    x = utility.array_of_comm(c1, num_comm_c1)
    y = utility.array_of_comm(c2, num_comm_c2)
    # Compute the entropy of each cover H(X), H(Y)
    h_xi, h_x = _cover_entropy(x, num_vtx)
    h_yj, h_y = _cover_entropy(y, num_vtx)
    # Initialize the overlap matrix, containing how many vertices shares communities i, y from covers c1, c2
    overlap_mat = np.ndarray((len(x), len(y)), dtype=int)
    for i in range(len(x)):
        for j in range(len(y)):
            overlap_mat[i][j] = len(x[i] & y[j])
    # Compute vectors H(Xi|Y), H(Yj|X), find the best "given" community that minimize the entropy
    h_xi_given_y = np.full(len(x), float(num_vtx))
    h_yj_given_x = np.full(len(y), float(num_vtx))
    for i in range(len(x)):
        for j in range(len(y)):
            # Compute how many vertices shares communities i, j from covers c1, c2
            h_x0y0 = _h(num_vtx - len(x[i]) - len(y[j]) + overlap_mat[i][j], num_vtx)
            h_x0y1 = _h(len(y[j]) - overlap_mat[i][j], num_vtx)
            h_x1y0 = _h(len(x[i]) - overlap_mat[i][j], num_vtx)
            h_x1y1 = _h(overlap_mat[i][j], num_vtx)
            if h_x0y0 + h_x1y1 >= h_x0y1 + h_x1y0:
                h_xi_joint_yj = h_x0y0 + h_x0y1 + h_x1y0 + h_x1y1
                h_star_xi_given_yj = h_xi_joint_yj - h_yj[j]
                h_star_yj_given_xi = h_xi_joint_yj - h_xi[i]
            else:
                h_star_xi_given_yj = h_xi[i]
                h_star_yj_given_xi = h_yj[j]
            h_xi_given_y[i] = h_xi_given_y[i] if h_xi_given_y[i] < h_star_xi_given_yj else h_star_xi_given_yj
            h_yj_given_x[j] = h_yj_given_x[j] if h_yj_given_x[j] < h_star_yj_given_xi else h_star_yj_given_xi
    # Compute H(X|Y), H(Y|X), summing vectors H(Xi|Y) and H(Yj|X)
    h_x_given_y = np.sum(h_xi_given_y)
    h_y_given_x = np.sum(h_yj_given_x)
    mut_info = (h_x - h_x_given_y + h_y - h_y_given_x) / 2
    return mut_info / max(h_x, h_y)


def omega(c1: gt.VertexPropertyMap, c2: gt.VertexPropertyMap):
    graph = c1.get_graph()
    num_pairs = graph.num_vertices() * (graph.num_vertices() - 1) / 2
    # Computing unadjusted Omega index (omega_u) and expected Omega index in the null model (omega_e)
    omega_u, omega_e = 0, 0
    num_pairs_c1 = {}
    num_pairs_c2 = {}
    for v1, v2 in combinations(graph.get_vertices(), 2):
        # Number of communities shared by (v1, v2) in c1 and c2
        c1_j = len(c1[v1] & c1[v2])
        c2_j = len(c2[v1] & c2[v2])
        # OmegaU: For each pair, increment omega_u if in both covers the two vertex shares j communities
        if c1_j == c2_j:
            omega_u += 1
        # OmegaE: For each pair that in cover c shares j communities, increment num_pairs_c[j]
        num_pairs_c1[c1_j] = num_pairs_c1.get(c1_j, 0) + 1
        num_pairs_c2[c2_j] = num_pairs_c2.get(c2_j, 0) + 1
    for j in num_pairs_c1:
        omega_e += num_pairs_c1[j] * num_pairs_c2.get(j, 0)
    # Dividing for the number of pairs
    omega_u /= num_pairs
    omega_e /= num_pairs ** 2
    # Returning Omega index
    return (omega_u - omega_e) / (1 - omega_e) if omega_e != 1 else 1.0


def omega_wrong(c1: gt.VertexPropertyMap, c2: gt.VertexPropertyMap):
    graph = c1.get_graph()
    num_vertices = graph.num_vertices()
    num_pairs = num_vertices * (num_vertices - 1) / 2
    # num_v_c1[j] is the number of vertices belonging to j communities in c1
    num_v_c1 = {}
    # num_v_c2[j] is the number of vertices belonging to j communities in c1
    num_v_c2 = {}
    # num_v_c1_c2[j] is the number of vertices belonging to j communities in both c1 and c2
    num_v_c1_c2 = {}
    for vertex in graph.get_vertices():
        c1_j = len(c1[vertex])
        c2_j = len(c2[vertex])
        # print(f"[Node {vertex}] c1_j: {c1_j}, c2_j {c2_j}")
        num_v_c1[c1_j] = num_v_c1.get(c1_j, 0) + 1
        num_v_c2[c2_j] = num_v_c2.get(c2_j, 0) + 1
        if c1_j == c2_j:
            num_v_c1_c2[c1_j] = num_v_c1_c2.get(c1_j, 0) + 1
    # Computing unadjusted Omega index (omega_u)
    omega_u = 0
    for j in num_v_c1_c2:
        # Add the number of couples that belongs to j comm in both c1 and c2
        omega_u += num_v_c1_c2[j] * (num_v_c1_c2[j] - 1) / 2
    omega_u /= num_pairs
    # Computing expected Omega index in the null model (omega_e)
    omega_e = 0
    for j in num_v_c1:
        pairs_c1 = num_v_c1[j] * (num_v_c1[j] - 1) / 2
        pairs_c2 = num_v_c2.get(j, 0) * (num_v_c2.get(j, 0) - 1) / 2
        # Add the number of couples that belongs to j comm in both c1 and c2
        omega_e += pairs_c1 * pairs_c2
    omega_e /= num_pairs ** 2
    return (omega_u - omega_e) / (1 - omega_e)
