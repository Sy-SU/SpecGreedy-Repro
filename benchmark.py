#!/usr/bin/env python3
"""benchmark.py — multi‑round evaluation for Charikar, Flow, SpecGreedy.

Workflow per round
------------------
1. **Generate** a random graph by invoking an external generator script
   (default: ``utils/generator.py``).
2. **Evaluate** three algorithms by invoking an external compare script
   (default: ``compare.py``) with CLI flags so its report goes to a predictable
   path (template supports ``%t`` = timestamp, ``{run}`` = round number).
3. **Parse** the `[TIME] TAG 用时 X.XXX 秒` lines from that report and keep a
   running total.
4. After *N* rounds, print the average runtime for each algorithm.

Key changes vs. the previous version
------------------------------------
* **Compare script is now executed via *subprocess*** instead of an
  ``importlib`` call, making it trivial to pass ``--out`` and other flags.
* New CLI flags:
  - ``--compare-script``: path to the compare driver (default: ``compare.py``)
  - ``--compare-out``:  template for the compare report path; may contain
    ``%t`` (strftime timestamp) and ``{run}`` placeholder.
  - ``--k`` / ``--sg-method``: forwarded to *SpecGreedy*.
* The default ``--compare-out`` preserves the old behaviour of a distinct
  timestamped file for every round, so **no data is ever overwritten**.

Usage example
-------------
```bash
python benchmark.py \
    --nodes 50 --edges 300 --runs 200 \
    --generator utils/generator.py \
    --compare-script compare.py \
    --graph-out data/graph.txt \
    --compare-out outs/bench_%t_run{run}.txt \
    --k 10 --sg-method Charikar --seed 123
```
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict

TIME_RE = re.compile(r"\[TIME] (\w+) 用时 ([\d.]+) 秒")

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def build_gen_cmd(args: argparse.Namespace) -> list[str]:
    cmd = [
        "python",
        args.generator,
        "--nodes", str(args.nodes),
        "--edges", str(args.edges),
        "--out", args.graph_out,
    ]
    if args.seed is not None:
        cmd += ["--seed", str(args.seed)]
    return cmd

def build_cmp_cmd(args: argparse.Namespace, run_id: int) -> tuple[list[str], Path]:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = args.compare_out.replace("%t", ts).replace("{run}", str(run_id))
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "python",
        args.compare_script,
        "--graph", args.graph_out,
        "--out", str(out_path),
        "--k", str(args.k),
        "--sg-method", args.sg_method,
    ]
    return cmd, out_path


def parse_time_lines(report: Path, totals: Dict[str, float]):
    with report.open(encoding="utf-8") as fp:
        for line in fp:
            m = TIME_RE.match(line.strip())
            if m:
                tag, sec = m.group(1), float(m.group(2))
                totals[tag] = totals.get(tag, 0.0) + sec

# ---------------------------------------------------------------------------
# Main routine
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser("Benchmark Charikar, Flow, SpecGreedy on random graphs")
    ap.add_argument("-n", "--nodes", type=int, default=30, help="#vertices (default 30)")
    ap.add_argument("-e", "--edges", type=int, default=200, help="#edges (default 200)")
    ap.add_argument("-r", "--runs",  type=int, default=100, help="#rounds (default 100)")

    ap.add_argument("--generator", default="utils/generator.py", help="graph generator script")
    ap.add_argument("--compare-script", default="compare.py", help="compare driver script")

    ap.add_argument("--graph-out", default="data/graph.txt", help="temp graph file path")
    ap.add_argument("--compare-out", default="outs/compare_%t_run{run}.txt",
                    help="report path template for compare.py (%t = time, {run} = round)")

    ap.add_argument("--k", type=int, default=10, help="k for SpecGreedy (default 10)")
    ap.add_argument("--sg-method", default="Charikar", help="method for SpecGreedy")

    ap.add_argument("--seed", type=int, help="fixed RNG seed (optional)")

    args = ap.parse_args()

    totals: Dict[str, float] = {}

    for run in range(1, args.runs + 1):
        print(f"\n=== Round {run}/{args.runs} ===")

        # 1) Generate graph
        args.seed = time.perf_counter_ns() // 1000000
        subprocess.run(build_gen_cmd(args), check=True)

        # 2) Run compare script
        cmp_cmd, report_path = build_cmp_cmd(args, run)
        t0 = time.perf_counter()
        subprocess.run(cmp_cmd, check=True)
        print(f"[INFO] compare.py 用时 {time.perf_counter() - t0:.3f} 秒 → {report_path}")

        # 3) Accumulate times
        parse_time_lines(report_path, totals)

    # ---------- summary ----------
    print("\n=========== 平均用时 ===========")
    for tag, total in sorted(totals.items()):
        print(f"{tag:<10}: {total / args.runs:.4f} 秒")


if __name__ == "__main__":
    main()
