import graph_tool.all as gt
import numpy as np
import analysis
import algorithms
import evaluation


# with open("data/informations.txt", 'a') as info:
#     for g_name in ["youtube-no2.gt"]:
#         g = gt.load_graph(f"graphs/{g_name}")
#         info.write(f"{g_name[:g_name.find('.')]}\t\t")
#         info.write("filter-no2\t")
#         info.write(f"{g.num_vertices()}\t")
#         info.write(f"{g.num_edges()}\t")
#         info.write(f"{g.gp.num_comm}\t")
#         cc = gt.label_components(g)[0].get_array()
#         cc_count = np.bincount(cc)
#         info.write(f"{cc_count.size}\t")
#         info.write(f"{np.quantile(cc_count, 0.1):.3f}\t")
#         info.write(f"{np.quantile(cc_count, 0.5):.3f}\t")
#         info.write(f"{np.quantile(cc_count, 0.9):.3f}\t")
#         o_min, o_max, o_mean = analysis.comm_membership(g.vp.comm)
#         info.write(f"{o_min}\t{o_max}\t{o_mean:.3f}\t")
#         c_min, c_max, c_mean = analysis.comm_size(g.vp.comm, g.gp.num_comm)
#         info.write(f"{c_min}\t{c_max}\t{c_mean:.3f}\n")
#         info.flush()

with open("data/mixed.txt", 'a') as perf:
    for g_name, truth_o_max in [("youtube-no2.gt", 13)]:
        g = gt.load_graph(f"graphs/{g_name}")
        for i in range(4):
            threshold = 0.01 + (1 / (1+truth_o_max) - 0.01)*i/3
            perf.write(f"{g_name[:g_name.find('-')]}\t\t")
            perf.write("filter-no2\t\t")
            perf.write("SLPA\t\t")
            perf.write(f"{threshold:.3f}\t\t")
            perf.write(f"100\t\t")
            communities, num_comm = algorithms.slpa(g, threshold=threshold)
            perf.write(f"{evaluation.omega(g.vp.comm, communities):.3f}\t")
            perf.write(f"{evaluation.nmi_max(g.vp.comm, g.gp.num_comm, communities, num_comm):.3f}\t")
            perf.write(f"{evaluation.f_score(g.vp.comm, communities):.3f}\t")
            perf.write(f"{num_comm}\t")
            o_min, o_max, o_mean = analysis.comm_membership(communities)
            perf.write(f"{o_min}\t{o_max}\t{o_mean:.3f}\t")
            c_min, c_max, c_mean = analysis.comm_size(communities, num_comm)
            perf.write(f"{c_min}\t{c_max}\t{c_mean:.3f}\n")
            perf.flush()
