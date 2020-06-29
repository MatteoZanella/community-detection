import random
import math
import numpy as np
import graph_tool.all as gt
import utility


def slpa(graph: gt.Graph, iterations=100, threshold=0.1, strictness=0):
    # Initialization of the memory list for each node O(n)
    memory = [[vtx] for vtx in graph.get_vertices()]
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
    communities = auto_postprocessing(graph, memory, strictness, threshold)
    # Return a dictionary where a set of communities labels is associated to each node key
    # The result is normalized such that community labels belongs to [0, num_comm]
    num_comm = utility.normalize(communities)
    return communities, num_comm


# Vb is this algorithm with the initial sorting for the vertex grade
def slpa_a(graph: gt.Graph, iterations=100, min_strength=0.5, threshold=0.05, strictness=1/3):
    # Define degrees for label strength property
    out_degrees = graph.get_out_degrees(graph.get_vertices())
    max_degree = np.quantile(out_degrees, 0.99, interpolation='lower')
    def strength(vtx: int):
        return 1 if out_degrees[vtx] >= max_degree else (1 - min_strength) / max_degree * out_degrees[vtx] + min_strength
    # Initialization of the memory list for each node O(n)
    memory = [[vtx] for vtx in graph.get_vertices()]
    # T iterations for filling up nodes memory based on speaking and listening rules
    # traversal_list = np.argsort(-out_degrees)
    for _ in range(iterations):
        for listener in np.random.permutation(graph.get_vertices()):
        # for listener in traversal_list:
            labels_freq = {}
            for speaker in graph.get_out_neighbors(listener):
                # Speaking rule: Speaker selects a random label from his memory with chances or re-extraction
                while True:
                    spoken_label = random.choice(memory[speaker])
                    if random.random() < strength(spoken_label):
                        break
                labels_freq[spoken_label] = labels_freq.get(spoken_label, 0) + 1
            # Listening rule: Listener adds the most popular label to its memory and choose the strongest in case of tie
            max_label = -1
            max_freq = 0
            for label in labels_freq:
                if labels_freq[label] > max_freq or (labels_freq[label] == max_freq and strength(label) > strength(max_label)):
                    max_label = label
                    max_freq = labels_freq[label]
            if max_freq > 0:
                memory[listener].append(max_label)
    # Post-processing operation to keep in memory only the most used labels, given the parametric threshold
    communities = auto_postprocessing(graph, memory, strictness, threshold)
    # Return a dictionary where a set of communities labels is associated to each node key
    # The result is normalized such that community labels belongs to [0, num_comm]
    num_comm = utility.normalize(communities)
    return communities, num_comm


def classic_postprocessing(graph: gt.Graph, memory, threshold):
    communities = graph.new_vertex_property("object")
    for vtx, labels in enumerate(memory):
        memory_freq = {}
        num_labels = len(labels)
        for label in labels:
            memory_freq[label] = memory_freq.get(label, 0) + 1
        communities[graph.vertex(vtx)] = {label for label in memory_freq if memory_freq[label] / num_labels >= threshold}
    return communities


def auto_postprocessing(graph: gt.Graph, memory, strictness=1/3, threshold=0.0):
    communities = graph.new_vertex_property("object")
    for vtx, labels in enumerate(memory):
        memory_freq = {}
        max_freq = 0
        for label in labels:
            memory_freq[label] = memory_freq.get(label, 0) + 1
            max_freq = max_freq if max_freq > memory_freq[label] else memory_freq[label]
        min_accepted_freq = max(math.floor(max_freq * strictness), threshold * len(labels))
        communities[graph.vertex(vtx)] = {label for label in memory_freq if memory_freq[label] >= min_accepted_freq}
    return communities


def statistical_inference(graph: gt.Graph):
    state = gt.minimize_blockmodel_dl(graph)
    blocks = state.get_blocks()
    communities = graph.new_vp("object")
    for v in graph.get_vertices():
        communities[v] = {blocks[v]}
    num_comm = utility.normalize(communities)
    return communities, num_comm
