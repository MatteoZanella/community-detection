import graph_tool.all as gt
from itertools import combinations


def NMI_max():
    return 0


def omega(c1: gt.VertexPropertyMap, c2: gt.VertexPropertyMap):
    graph = c1.get_graph()
    num_vertices = graph.num_vertices()
    num_pairs = num_vertices * (num_vertices - 1) / 2
    # Computing unadjusted Omega index (omega_u)
    # Computing expected Omega index in the null model (omega_e)
    omega_u = 0
    omega_e = 0
    agree_pairs_c1 = {}
    agree_pairs_c2 = {}
    for v1, v2 in combinations(graph.get_vertices(), 2):
        c1_agree, c1_j = len(c1[v1]) == len(c1[v2]), len(c1[v1])
        c2_agree, c2_j = len(c2[v1]) == len(c2[v2]), len(c2[v1])
        # OmegaU: For each pair, increment omega_u if in both covers both vertex belongs to j communities
        if c1_agree and c2_agree and c1_j == c2_j:
            omega_u += 1
        # OmegaE: For each pair, increment agree_pairs_c[j] if in the cover c they both belongs to j communities
        if c1_agree:
            agree_pairs_c1[c1_j] = agree_pairs_c1.get(c1_j, 0) + 1
        if c2_agree:
            agree_pairs_c2[c2_j] = agree_pairs_c2.get(c2_j, 0) + 1
    smaller_agree_pairs = agree_pairs_c1 if len(agree_pairs_c1) < len(agree_pairs_c2) else agree_pairs_c2
    for j in smaller_agree_pairs:
        omega_e += agree_pairs_c1[j] * agree_pairs_c2[j]
    omega_u /= num_pairs
    omega_e /= num_pairs**2
    # Returning Omega index
    return (omega_u - omega_e) / (1 - omega_e)
