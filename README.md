# Implementation and Experimentation of Algorithms for Overlapping Community Detection [![Read the Thesis](https://img.shields.io/badge/Read%20the%20Thesis-PDF-blue)](./Bachelor_Thesis_Community_Detection.pdf)

This repository contains the code and resources related to my thesis on community detection in graphs, with a focus on overlapping communities. The thesis explores existing algorithms, implements state-of-the-art methods, investigates potential improvements, and evaluates them using identified metrics. The implementations are written in Python.

## Overview

Many real-world graphs can be divided into communities, which are sets of nodes with more connections among themselves than with the rest of the graph. Identifying these communities provides insights into the graph's organization and the roles of its nodes. Overlapping communities, where nodes can belong to multiple communities, often provide a more accurate model of reality. However, their advantages over disjoint communities are still debated.

## Objectives

- Analyze existing community detection algorithms.
- Implement state-of-the-art algorithms.
- Investigate and propose potential improvements.
- Evaluate the algorithms using specific similarity metrics.

## Algorithms and Metrics

The absence of a precise definition of communities and overlapping nodes has led to the development of diverse algorithms. Older algorithms often use cliques, focusing on high internal edge density. Modern definitions consider both internal interconnection and separation from the rest of the network, often based on the probability of an edge existing between two nodes.

- **SLPA (Speaker-Listener Label Propagation Algorithm):** This is the best-performing algorithm at the time of anaysis, where community labels compete during propagation through nodes, which retain memory of updates to accumulate knowledge over iterations. Only labels with a frequency above a certain threshold are retained in post-processing.

### Proposed Heuristics

- **SLPAdeg:** An heuristic where labels initialized at high-degree nodes are retransmitted with higher probability, assuming these nodes are central to their community.

- **SLPAstrict:** Modifies the post-processing phase to retain only communities whose frequency exceeds a fraction (strictness) of the highest frequency community, considering frequencies relatively rather than absolutely.

### Evaluation Metrics

- **Normalized Mutual Information (NMI):** Based on mutual information.
- **Omega Index:** Based on cluster pairing.
- **F-score:** Measures precision in identifying overlapping nodes.

## Experiments

The algorithms were evaluated on four undirected graphs empirically divided into communities by Stanford researchers, with additional processing resulting in six graphs. Each graph reacts differently to changes in the threshold parameter, with a single point of maximum performance. SLPAdeg did not show improvements over SLPA, possibly due to high-degree nodes being points of high overlap. SLPAstrict generally performed better or similarly to SLPA, with the heuristic allowing for better performance, though parameters must be chosen somewhat arbitrarily.

## Future Work

Further exploration is needed to test the heuristics on other graphs, including artificial ones, and to attempt making the algorithm non-parametric, such as assigning different strictness values based on node degree.

## Requirements

- Python 3.x
- Required libraries: numpy, [graph_tool](https://graph-tool.skewed.de/)

## Usage

1. Clone the repository.
2. Install the required libraries (A Conda environment is recommended).
3. Download the graph text files from the [Stanford Large Network Dataset Collection](https://snap.stanford.edu/data/index.html#communities)
4. Run the `convert-graph.py` script to covert the plaintext graphs into a more efficient binary format.
  ```bash
  python ./convert-graph.py graph.txt [--directed] [--communities communities.txt] [--labels] [--reduce]
  ```
5. Run the `testing.py` script to test the algorithm and the heuristics.
  ```bash
  python ./testing.py
  ```
