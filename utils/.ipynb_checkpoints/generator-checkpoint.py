#!/usr/bin/env python3
"""Graph data generator (0‑indexed)

Generates an **undirected simple weighted graph** (no self‑loops, no parallel
edges) using **0‑based vertex indices** and optionally embeds dense subgraphs.

Output format:
    line 1: n m               # number of nodes and edges
    line 2: w0 w1 ... w{n-1}  # node weights (here always 1)
    next m lines: u v w       # undirected edge with weight w (0 ≤ u < v < n)

Example:
    python utils/generator.py --nodes 30 --edges 200 --out data/graph.txt --seed 42

CLI arguments:
    --nodes/-n      : number of vertices (n)
    --edges/-e      : number of edges (m)
    --out           : output file path (stdout if omitted)
    --seed          : RNG seed (optional, int)
    --clusters      : approx. number of dense clusters to embed (default: n//6)
    --density       : internal edge density of dense clusters (0‑1, default 0.8)
    --edge-weight/-w: edge weight (constant for all edges, default 1)

The script first embeds dense clusters, then fills the remaining edge budget
uniformly at random.
"""
from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path
from typing import List, Set, Tuple

Edge = Tuple[int, int]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Simple weighted graph generator with dense regions (0‑indexed)")
    p.add_argument("--nodes", "-n", type=int, required=True, help="Number of nodes (n)")
    p.add_argument("--edges", "-e", type=int, required=True, help="Number of edges (m)")
    p.add_argument("--out", type=str, default="-", help="Output file (default: stdout)")
    p.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")
    p.add_argument("--clusters", type=int, default=None, help="Approx. number of dense clusters")
    p.add_argument("--density", type=float, default=0.8, help="Internal edge density of clusters [0, 1]")
    p.add_argument("--edge-weight", "-w", type=int, default=1, help="Edge weight (constant, default 1)")
    args = p.parse_args()

    if args.nodes < 1:
        p.error("--nodes must be >= 1")
    max_edges = args.nodes * (args.nodes - 1) // 2
    if not (0 <= args.edges <= max_edges):
        p.error(f"--edges must be between 0 and {max_edges} for n={args.nodes}")
    if not (0.0 <= args.density <= 1.0):
        p.error("--density must be in [0, 1]")
    return args


def add_edge(edges: Set[Edge], u: int, v: int) -> None:
    """Insert an undirected edge (u,v) into *edges* if valid."""
    if u == v:
        return  # no self‑loops
    a, b = (u, v) if u < v else (v, u)
    edges.add((a, b))


def generate_dense_cluster(nodes: List[int], density: float, edges: Set[Edge]) -> None:
    """Add edges to form a dense subgraph among the given 0‑indexed nodes."""
    s = len(nodes)
    if s < 2:
        return
    possible_pairs = [(nodes[i], nodes[j]) for i in range(s) for j in range(i + 1, s)]
    random.shuffle(possible_pairs)
    target = int(round(density * len(possible_pairs)))
    for u, v in possible_pairs[:target]:
        add_edge(edges, u, v)


def fill_random_edges(n: int, edges: Set[Edge], m: int) -> None:
    """Add random edges until |edges| == m (0‑indexed vertices)."""
    while len(edges) < m:
        u = random.randrange(n)
        v = random.randrange(n)
        add_edge(edges, u, v)


def pick_clusters(n: int, approx_k: int) -> List[List[int]]:
    """Return a list of node lists representing clusters (0‑indexed)."""
    remaining = list(range(n))
    random.shuffle(remaining)
    clusters: List[List[int]] = []
    k = max(1, approx_k)
    for _ in range(k):
        if not remaining:
            break
        # Cluster size between 3 and min(8, remaining)
        size = random.randint(3, min(8, len(remaining))) if n >= 6 else len(remaining)
        cluster = [remaining.pop() for _ in range(size)]
        clusters.append(cluster)
    return clusters


def main() -> None:
    args = parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    n, m = args.nodes, args.edges
    edges: Set[Edge] = set()

    # 1) Choose dense clusters
    approx_clusters = args.clusters if args.clusters is not None else max(1, n // 6)
    clusters = pick_clusters(n, approx_clusters)

    # 2) Embed dense clusters
    for cluster in clusters:
        generate_dense_cluster(cluster, args.density, edges)
        if len(edges) >= m:
            break

    # 3) Fill remaining edge budget randomly
    fill_random_edges(n, edges, m)

    # Sanity check
    assert len(edges) == m, "Edge count mismatch after generation"

    # 4) Prepare output
    out_path = Path(args.out)
    out_stream = sys.stdout if args.out == "-" else out_path.open("w", encoding="utf‑8")
    try:
        print(f"{n} {m}", file=out_stream)
        print(" ".join(["1"] * n), file=out_stream)  # node weights
        for u, v in sorted(edges):
            print(f"{u} {v} {args.edge_weight}", file=out_stream)
    finally:
        if out_stream is not sys.stdout:
            out_stream.close()


if __name__ == "__main__":
    main()
