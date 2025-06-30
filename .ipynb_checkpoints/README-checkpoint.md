# SpecGreedy — Quick‑Start Guide

> **目录**
>
> 1. [准备工作](#准备工作)
> 2. [一次性比较（compare.py）](#一次性比较comparepy)
> 3. [Benchmark — 高密度图](#benchmark--高密度图)
> 4. [Benchmark — 完全随机图](#benchmark--完全随机图)
> 5. [单独运行各算法](#单独运行各算法)
> 6. [直接生成一张随机图](#直接生成一张随机图)

---

## 准备工作

```bash
# 克隆/进入仓库后，建议先创建虚拟环境
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 安装依赖（如果已维护 requirements.txt）
pip install -r requirements.txt

# 切到项目根目录
cd ~/SpecGreedy
```

---

## 一次性比较（compare.py）

```bash
# 读取现有 data/graph.txt，结果追加到 outs/bench_run1.txt
python compare.py \
  --graph data/graph.txt \
  --out   outs/bench_run1.txt \
  --k     10 \
  --sg-method Charikar
```

* 输出文件中含三行形如 `[TIME] CHARIKAR 用时 …` 的统计，可供后续解析。\*

---

## Benchmark — 高密度图

> 通过 **`utils/generator.py`** 先嵌入稠密子图，再随机补边。

```bash
python benchmark.py \
  --nodes 500 --edges 3000 --runs 10 \
  --generator utils/generator.py \
  --compare-script compare.py \
  --graph-out data/graph.txt \
  --compare-out outs/benchmark_test/run{run}.txt \
  --k 10 --sg-method Charikar
```

*`{run}` 会被替换为轮次编号；每轮写入独立的 report。*

---

## Benchmark — 完全随机图

> 使用 **`utils/generator_random.py`** 从完全图中均匀采样边，无稠密聚簇偏置。

```bash
python benchmark.py \
  --nodes 50 --edges 100 --runs 10 \
  --generator utils/generator_random.py \
  --compare-script compare.py \
  --graph-out data/graph.txt \
  --compare-out outs/benchmark_test/run{run}.txt \
  --k 10 --sg-method Charikar
```

---

## 单独运行各算法

```bash
python SpecGreedy.py   # 光谱+贪心
python Flow.py         # 网络流
python Charikar.py     # 贪心
```

*各脚本默认读取 `data/graph.txt` 并将结果写入自带的 outs/ 目录。*

---

## 直接生成一张随机图

```bash
# 均匀随机图，0‑index，无自环、平行边
python utils/generator_random.py -n 10 -e 20 --out data/graph.txt
```

生成文件格式：

1. 第一行 `n m`
2. 第二行 `n` 个节点权（默认 1）
3. 余下 `m` 行 `u v w`（统一边权，默认 1）。

---

如需更多选项（随机种子、边权、稠密簇密度等），请查看各脚本 `--help` 输出！

## License and Attribution

This repository reproduces the implementation from [wenchieh/specgreedy](https://github.com/wenchieh/specgreedy), originally licensed under the MIT License.

All credit for the original implementation goes to the authors of that repository. This fork/adaptation retains the same license.

See [LICENSE](LICENSE) for details.
