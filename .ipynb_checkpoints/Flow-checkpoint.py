# densest_subgraph_flow.py  —— Dinic 版
import math
import networkx as nx

try:
    from networkx.algorithms.flow import dinic as maxflow_alg
except ImportError:
    from networkx.algorithms.flow import dinitz as maxflow_alg


# ---------- 读图 ----------
def read_graph(path):
    with open(path) as f:
        n, m = map(int, f.readline().split())
        _ = f.readline()                 # 节点权行，此算法用不到
        edges = [tuple(map(int, f.readline().split()[:2])) for _ in range(m)]
    return n, m, edges

# ---------- 构造流网络 ----------
def build_flow_network(n, m, edges, lam, deg):
    Gf = nx.DiGraph()
    s, t = "s", "t"
    Gf.add_nodes_from(range(n))
    Gf.add_node(s)
    Gf.add_node(t)

    # 无向边 → 两条容量 1 的有向边
    for u, v in edges:
        Gf.add_edge(u, v, capacity=1)
        Gf.add_edge(v, u, capacity=1)

    for u in range(n):
        Gf.add_edge(s, u, capacity=m)                        # s→u
        cap = m + 2 * lam - deg[u]
        Gf.add_edge(u, t, capacity=max(0, cap))              # u→t

    return Gf, s, t

# ---------- 主函数 ----------
def densest_subgraph_exact(path, eps=0.1):
    n, m, edges = read_graph(path)
    deg = [0] * n
    for u, v in edges:
        deg[u] += 1
        deg[v] += 1

    l, r = 0.0, float(m)
    best_S = set(range(n))

    while r - l > eps:
        lam = (l + r) / 2
        Gf, s, t = build_flow_network(n, m, edges, lam, deg)

        # === Dinic 最小割 ===
        cut_val, (S_side, T_side) = nx.minimum_cut(Gf, s, t, flow_func=maxflow_alg)

        V1 = S_side - {s}
        if V1:
            l = lam          # g(V1) ≥ λ
            best_S = V1
        else:
            r = lam

    # 重新精确计算密度
    sub_edges = sum(1 for u, v in edges if u in best_S and v in best_S)
    density = sub_edges / len(best_S)
    return density, best_S

def eval(graph_path, output_path):
    dens, S = densest_subgraph_exact(graph_path)
    result = f"[Flow] 密度 {dens} 最密点集 {sorted(S)}\n"

    with open(output_path, "a") as f:
        f.write(result)


if __name__ == "__main__":
    path = "data/graph.txt"
    dens, S = densest_subgraph_exact(path)
    
    print(f"[Flow] 最密点集 {sorted(S)}, 密度 {dens}")