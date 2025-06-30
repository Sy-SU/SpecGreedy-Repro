# SpecGreedy.py
import argparse
from utils.graph import Graph
from utils.greedy import greedy
from sksparse.cholmod import cholesky
from scipy.sparse import random, csr_matrix, identity, diags
from scipy.sparse.linalg import svds
import numpy as np

def SpecGreedy(graph_path, k, method="Charikar"):
    G = Graph(graph_path)
    # G.print_info()

    A = csr_matrix(G.to_adjacency_matrix())
    n = A.shape[0]
    # print("Adjacency matrix:")
    # print(A)
    
    # 辅助量
    deg_vec = np.asarray(A.sum(axis=1)).flatten()      # 节点度 (length n)
    D       = diags(deg_vec, format="csr")             # 度矩阵
    I_n     = identity(n, format="csr")                # 单位阵

    # 默认
    P, Q = A, I_n
    L = list(range(n))      # 默认非二分图

    method = method.lower()   # 忽略大小写

    if method == "minquotientcut":
        # P =  -Laplacian  = A - D ,   Q = I
        P = A - D
        Q = I_n
    elif method == "charikar":
        # P = A ,  Q = I
        P = A
        Q = I_n
    elif method == "fraudar":
        D_w = G.weight_diag()
        P = A + 2 * D_w    
        Q = I_n
    elif method == "sparsecutds":
        # P = A - (2α / (2α+1)) D ,  Q = I
        alpha = 1.0                    # 可设成其他 α
        coeff = (2 * alpha) / (2*alpha + 1)
        P = A - coeff * D
        Q = I_n
    elif method == "risk-averse ds":
        # A = A+  - A- ，将正负部分分开
        A_plus  = A.maximum(0)
        A_minus = (-A).maximum(0)
        lambda1 = 1.0
        lambda2 = 1.0
        P = A_plus  + lambda1 * I_n
        Q = A_minus + lambda2 * I_n
    else:
        print(f"[WARN] 未识别 method '{method}', 默认用 Charikar (P=A, Q=I).")
        P = A
        Q = I_n
    
    # SVD分解：取前k个奇异值
    U, SIGMA, Vt = svds(A, k=k, which="LM")

    # 翻转顺序（svds返回的是升序）
    U = U[:, ::-1]
    SIGMA = SIGMA[::-1]
    Vt = Vt[::-1, :]

    # 打印结果
    # print("Left Singular Vectors (U):\n", U)
    # print("Singular Values (SIGMA):\n", SIGMA)
    # print("Right Singular Vectors (V):\n", Vt.T)
    
    # 初始化最优子集和最优密度
    S = []
    best_score = 0.0
    
    for i in range(0, k):
        threshold = 1 / np.sqrt(len(L))  # 这里L和R大小一样

        u_vec = U[:, i]
        v_vec = Vt.T[:, i]

        # 选出u分量大的节点
        S_u = [idx for idx, val in enumerate(u_vec) if val > threshold]
        # 选出v分量大的节点
        S_v = [idx for idx, val in enumerate(v_vec) if val > threshold]

        # 合并去重
        S_r = list(sorted(set(S_u + S_v)))

        # print(f"\n[Singular Vector {i+1}]")
        # print("Threshold:", threshold)
        # print("Nodes from u:", S_u)
        # print("Nodes from v:", S_v)
        # print("Candidate node set S_r:", S_r)
        
        # 输出诱导子图
        A_sub = A[S_r, :][:, S_r]
        # print("Induced subgraph adjacency matrix:")
        # print(A_sub.toarray())
        
        # 在循环里对S_r对应的子图：
        A_sub = A[S_r, :][:, S_r]
        P_sub = P[S_r, :][:, S_r]
        Q_sub = Q[S_r, :][:, S_r]

        score, node_set = greedy(A_sub, P_sub, Q_sub)
        
        if best_score < score:
            best_score = score
            S = node_set
            
        if i + 1 < k and best_score >= SIGMA[i + 1]:
            print(f"[INFO] 提前终止：best_score={best_score:.4f} >= σ[{i + 1}]={SIGMA[i + 1]:.4f}")
            break
    return S, best_score

def eval(graph_path, k, method, output_path):
    S, best_score = SpecGreedy(graph_path, k, method)
    result = f"[SPECGREEDY] 密度 {best_score} 最密点集 {sorted(S)}\n"

    with open(output_path, "a") as f:
        f.write(result)

    
if __name__ == "__main__":
    path = "data/graph.txt"
    S, best_score = SpecGreedy(path, 10)
    
    print(f"[SPECGREEDY] 最密点集 {S}, 密度 {best_score}")