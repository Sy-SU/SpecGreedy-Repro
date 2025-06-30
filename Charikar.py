# Charikar.py

import numpy as np
import heapq
from scipy.sparse import csr_matrix
from utils.graph import Graph

def charikar(graph_path: str):
    G = Graph(graph_path)
    # G.print_info()

    A_sparse = csr_matrix(G.to_adjacency_matrix())
    n = A_sparse.shape[0]
    nodes = set(range(n))

    # 初始度
    degrees = np.array(A_sparse.sum(axis=1)).flatten()

    # 小根堆
    heap = [(deg, idx) for idx, deg in enumerate(degrees)]
    heapq.heapify(heap)

    # 总边数（无向图要除2）
    total_edge_weight = A_sparse.sum() / 2.0

    best_score = -np.inf
    best_nodes = list(nodes)

    current_edge_weight = total_edge_weight

    while nodes:
        # 当前密度 = 边数 / 点数
        if len(nodes) > 0:
            # print(f"{current_edge_weight} {nodes}")
            score = current_edge_weight / len(nodes)
            if score > best_score:
                best_score = score
                best_nodes = list(nodes)

        # 从堆弹出度最小节点
        while heap:
            deg, v = heapq.heappop(heap)
            if v in nodes:
                break
        else:
            break  # 堆空

        # 更新：去掉v带来的边
        row = A_sparse.getrow(v)
        neighbors = row.indices
        weights = row.data
        for u, w in zip(neighbors, weights):
            if u in nodes:
                degrees[u] -= w
                current_edge_weight -= w
                heapq.heappush(heap, (degrees[u], u))

        nodes.remove(v)

    return best_score, best_nodes

def eval(graph_path, output_path):
    score, nodes = charikar(graph_path)
    result = f"[CHARIKAR] 密度 {score} 最密点集 {sorted(nodes)}\n"
    
    with open(output_path, "a") as f:
        f.write(result)

# 直接运行脚本：举个示例
if __name__ == "__main__":
    path = "data/graph.txt"
    score, nodes = charikar(path)
    print(f"[CHARIKAR] 最密点集 {nodes}, 密度 {score}")