#!/usr/bin/env python3
"""generator_random.py — uniform‑random simple weighted graph (0‑indexed)

Generates an undirected simple graph (no self‑loops, no parallel edges) where
all *m* edges are sampled **uniformly without replacement** from the complete
set of \(n(n-1)/2\) possible pairs.

Output format (identical to other tools):
    line 1: n m               # number of nodes and edges
    line 2: w0 w1 … w{n-1}    # vertex weights (here a constant)
    next m lines: u v w       # undirected edge with weight w (u < v)

CLI arguments
-------------
--nodes/-n        Number of vertices (n)              [required]
--edges/-e        Number of edges (m)                 [required]
--out             Output path ("-" → stdout)          [default "-"]
--seed            RNG seed (int).  If omitted, uses a **milliseconds precision**
                  monotonic timestamp so each run differs.
--edge-weight/-w  Constant weight for every edge      [default 1]

Notes
-----
* For sparse graphs (m < 0.4 * n(n-1)/2) we insert edges via a rejection‑free
  loop using a hash‑set.
* For dense graphs we first build & shuffle the full edge list once, which is
  faster when m is close to the maximum.
"""
from __future__ import annotations

import argparse
import random
import sys
import time
from pathlib import Path
from typing import List, Set, Tuple

Edge = Tuple[int, int]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Uniform random graph generator (0‑indexed)")
    p.add_argument("--nodes", "-n", type=int, required=True, help="Number of vertices (n)")
    p.add_argument("--edges", "-e", type=int, required=True, help="Number of edges (m)")
    p.add_argument("--out", type=str, default="-", help="Output file (default: stdout)")
    p.add_argument("--seed", type=int, default=None, help="Random seed (default: monotonic clock ms)")
    p.add_argument("--edge-weight", "-w", type=int, default=1, help="Edge weight (default 1)")
    args = p.parse_args()

    if args.nodes < 1:
        p.error("--nodes must be >= 1")
    total = args.nodes * (args.nodes - 1) // 2
    if not (0 <= args.edges <= total):
        p.error(f"--edges must be between 0 and {total} for n={args.nodes}")
    return args


def choose_seed(seed: int | None) -> int:
    """Return a concrete seed value (ms precision)"""
    if seed is not None:
        return seed
    # Use monotonic perf counter to avoid issues with wall‑clock jumps.
    return time.perf_counter_ns() // 1_000_000


def sample_edges(n: int, m: int) -> List[Edge]:
    """Uniformly sample *m* distinct undirected edges among n vertices."""
    total = n * (n - 1) // 2
    # Dense threshold: build list if selecting more than 40% of possible edges.
    if m > 0.4 * total:
        all_pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
        random.shuffle(all_pairs)
        return all_pairs[:m]

    edges: Set[Edge] = set()
    while len(edges) < m:
        u = random.randrange(n)
        v = random.randrange(n)
        if u == v:
            continue
        a, b = (u, v) if u < v else (v, u)
        edges.add((a, b))
    return list(edges)


def main() -> None:
    args = parse_args()

    # Determine seed.
    args.seed = choose_seed(args.seed)
    random.seed(args.seed)

    n, m = args.nodes, args.edges
    edges = sample_edges(n, m)
    assert len(edges) == m

    # Output
    out_path = Path(args.out)
    out_fp = sys.stdout if args.out == "-" else out_path.open("w", encoding="utf-8")
    try:
        print(f"{n} {m}", file=out_fp)
        print(" ".join(["1"] * n), file=out_fp)
        for u, v in sorted(edges):
            print(f"{u} {v} {args.edge_weight}", file=out_fp)
    finally:
        if out_fp is not sys.stdout:
            out_fp.close()


if __name__ == "__main__":
    main()
