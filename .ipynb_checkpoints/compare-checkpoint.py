#!/usr/bin/env python3
"""compare.py ‑‑ runtime & accuracy benchmark for Charikar, Flow, SpecGreedy
--------------------------------------------------------------------------
CLI‑driven replacement of the original hard‑coded script **without** passing
file handles to the *eval_* helpers (they expect paths).  This fixes the
`TypeError: expected str, bytes or os.PathLike` issue.

Output strategy
===============
1. First create/clear the report file.
2. Call each `eval_*` function with **str(out_path)** so they open in ``a``
   mode and append their own content.
3. Collect runtime statistics in‑memory, then append the three `[TIME]` lines
   at the end.

Usage examples
--------------
Mimic legacy behaviour:
```bash
python compare.py                # => outs/compare_<timestamp>.txt
```
Specify everything explicitly (for *benchmark.py* integration):
```bash
python compare.py \
  --graph data/graph.txt \
  --out   outs/bench_run1.txt \
  --k     10 \
  --sg-method Charikar
```

CLI flags
---------
  --graph / -g   PATH   Input graph (default: data/graph.txt)
  --out   / -o   PATH   Report file. If omitted, written to outs/compare_%t.txt
  --k                 k parameter forwarded to SpecGreedy (default: 10)
  --sg-method         method parameter for SpecGreedy (default: "Charikar")
"""
from __future__ import annotations

import argparse
import time
from datetime import datetime
from pathlib import Path

from SpecGreedy import eval as eval_specgreedy
from Flow       import eval as eval_flow
from Charikar   import eval as eval_charikar

TIME_LINE = "[TIME] {tag} 用时 {sec:.3f} 秒\n\n"

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser("Compare Charikar, Flow, and SpecGreedy algorithms")
    p.add_argument("--graph", "-g", default="data/graph.txt",
                   help="Input graph file (default: %(default)s)")
    p.add_argument("--out", "-o", default=None,
                   help="Output report file (default: outs/compare_%t.txt)")
    p.add_argument("--k", type=int, default=10,
                   help="k parameter passed to SpecGreedy (default: %(default)s)")
    p.add_argument("--sg-method", dest="sg_method", default="Charikar",
                   help="method parameter for SpecGreedy (default: %(default)s)")
    return p.parse_args()

def main() -> None:
    args = parse_args()

    # ---------- determine output path ----------
    if args.out is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = Path("outs") / f"compare_{ts}.txt"
    else:
        out_path = Path(args.out.replace("%t", datetime.now().strftime("%Y%m%d_%H%M%S")))
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"[INFO] Writing report to {out_path}")

    # Start with an empty file so the *eval_* helpers can append safely
    out_path.write_text("")

    timings = {}

    # ---------------- CHARIKAR -----------------
    print("[INFO] 开始评估 CHARIKAR...")
    t0 = time.perf_counter()
    eval_charikar(args.graph, str(out_path))
    timings["CHARIKAR"] = time.perf_counter() - t0

    # ---------------- FLOW ---------------------
    print("[INFO] 开始评估 FLOW...")
    t0 = time.perf_counter()
    eval_flow(args.graph, str(out_path))
    timings["FLOW"] = time.perf_counter() - t0

    # ---------------- SPECGREEDY ---------------
    print("[INFO] 开始评估 SPECGREEDY...")
    t0 = time.perf_counter()
    eval_specgreedy(args.graph, k=args.k, method=args.sg_method, output_path=str(out_path))
    timings["SPECGREEDY"] = time.perf_counter() - t0

    # ---------- append timing info ----------
    with out_path.open("a", encoding="utf-8") as fp:
        for tag, sec in timings.items():
            fp.write(TIME_LINE.format(tag=tag, sec=sec))

    print("[INFO] 所有评估完成，结果已保存到", out_path)


if __name__ == "__main__":
    main()
