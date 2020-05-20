import random
import numpy as np
import graph_tool.all as gt
import utility


def slpa(graph: gt.Graph, iterations=100, threshold=0.1):
    # Initialization of the memory list for each node O(n)
    memory = {vtx: [vtx] for vtx in graph.get_vertices()}
    # T iterations for filling up nodes memory based on speaking and listening rules
    for _ in range(iterations):
        for listener in np.random.permutation(graph.get_vertices()):
            labels_freq = {}
            for speaker in graph.get_out_neighbors(listener):
                # Speaking rule: Speaker selects a random label from his memory
                spoken_label = random.choice(memory[speaker])
                labels_freq[spoken_label] = labels_freq.get(spoken_label, 0) + 1
            # Listening rule: Listener adds the most popular label to its memory and choose randomly in case fo tie
            max_labels = []
            max_freq = 0
            for label in labels_freq:
                if labels_freq[label] == max_freq:
                    max_labels.append(label)
                elif labels_freq[label] > max_freq:
                    max_labels = [label]
                    max_freq = labels_freq[label]
            if max_freq > 0:
                memory[listener].append(random.choice(max_labels))
    # Post-processing operation to keep in memory only the most used labels, given the parametric threshold
    communities = graph.new_vertex_property("object")
    for node in memory:
        memory_freq = {}
        num_labels = len(memory[node])
        for label in memory[node]:
            memory_freq[label] = memory_freq.get(label, 0) + 1
        communities[graph.vertex(node)] = {label for label in memory_freq if memory_freq[label] / num_labels >= threshold}
    # Return a dictionary where a set of communities labels is associated to each node key
    # The result is normalized such that community labels belongs to [0, num_comm]
    num_comm = utility.normalize(communities)
    return communities, num_comm
