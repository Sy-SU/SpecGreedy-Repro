# greedy.py

import numpy as np
import heapq
from scipy.sparse import csr_matrix
from scipy.sparse import identity

def greedy(A_sparse, P, Q):
    n = A_sparse.shape[0]
    nodes = set(range(n))

    # 计算初始度
    degrees = np.array(A_sparse.sum(axis=1)).flatten()

    # 小根堆，元素 (deg, node)
    heap = [(deg, idx) for idx, deg in enumerate(degrees)]
    heapq.heapify(heap)

    best_score = -np.inf
    best_nodes = list(nodes)

    while nodes:
        # --- 1. 记录当前密度 -----------------
        x = np.zeros(n)
        x[list(nodes)] = 1.0

        Px = P @ x        # 稀疏×密：O(nnz(P_S))
        num = x @ Px

        if Q is identity(n, format="csr"):
            den = len(nodes)             # 直接计数
        else:
            Qx = Q @ x                   # 稀疏×密
            den = x @ Qx

        if den > 0:
            score = 0.5 * num / den
            if score > best_score:
                best_score = score
                best_nodes = list(nodes)

        # --- 2. 从堆里弹度最小节点 -------------
        while heap:
            deg, v = heapq.heappop(heap)
            if v in nodes:           # 确认有效
                break
        else:
            break                   # 堆空

        # 删除 v
        nodes.remove(v)

        # 更新 v 的邻居度数
        row = A_sparse.getrow(v).indices
        for u in row:
            if u in nodes:
                degrees[u] -= A_sparse[v, u]
                heapq.heappush(heap, (degrees[u], u))

    return best_score, best_nodes

if __name__ == "__main__":
    # 创建一个示例稀疏矩阵
    data = np.array([1, 2, 3, 4])
    row_idx = np.array([0, 0, 1, 2])
    col_idx = np.array([0, 2, 2, 3])

    A_example = csr_matrix((data, (row_idx, col_idx)), shape=(4, 4))

    # 调用打印函数
    print_sparse_matrix(A_example)
