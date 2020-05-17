import graph_tool.all as gt
from itertools import combinations


def NMI_max():
    return 0


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
    omega_e /= num_pairs**2
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
    omega_e /= num_pairs**2
    return (omega_u - omega_e) / (1 - omega_e)