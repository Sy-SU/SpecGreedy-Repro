from typing import List, Tuple
import numpy as np
from scipy.sparse import csr_matrix, diags

class Graph:
    def __init__(self, filename: str):
        self.n = 0              # 节点数
        self.m = 0              # 边数
        self.node_weights: List[float] = []
        self.edges: List[Tuple[int, int, float]] = []  # (u, v, w)

        self.load_from_file(filename)

    def load_from_file(self, filename: str):
        with open(filename, 'r') as f:
            # 1. 第一行 n m
            self.n, self.m = map(int, f.readline().split())

            # 2. 第二行点权
            self.node_weights = [0.0] + list(map(float, f.readline().split()))  # 下标从 1 开始

            if len(self.node_weights) != self.n + 1:
                raise ValueError("节点权数量与节点数不符")

            # 3. 后面 m 行是边
            for _ in range(self.m):
                u, v, w = f.readline().split()
                self.edges.append((int(u), int(v), float(w)))

    def print_info(self):
        print(f"Graph: n = {self.n}, m = {self.m}")
        print("Node weights:")
        for i in range(0, self.n):
            print(f"  Node {i}: {self.node_weights[i]}")
        print("Edges:")
        for u, v, w in self.edges:
            print(f"  ({u}, {v}) w = {w}")

    def to_adjacency_matrix(self):
        import numpy as np
        A = np.zeros((self.n, self.n))
        for u, v, w in self.edges:
            A[u][v] += w
            A[v][u] += w  # 无向边
        return A
    
    def weight_vector(self) -> np.ndarray:
        """
        返回大小为 n 的 NumPy 向量 w，w[i] 是节点 i 的权重
        （内部 self.node_weights 下标从 1 开始存放）
        """
        return np.array(self.node_weights[1:])

    def weight_diag(self) -> csr_matrix:
        """
        返回稀疏对角矩阵 D_w = diag(w1, w2, ..., wn)
        """
        return diags(self.weight_vector(), format="csr")
