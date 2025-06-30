# main.py
import argparse
from SpecGreedy import SpecGreedy

def main():
    parser = argparse.ArgumentParser(description="SpecGreedy SVD")
    parser.add_argument("--graph", type=str, default="data/graph.txt", help="Path to graph file")
    parser.add_argument("-k", type=int, default=10, help="Number of singular vectors")
    parser.add_argument("--method", type=str, default="Charikar",
                        help="Method name (e.g., Charikar, TempDS, Fraudar, Risk-averse DS, etc.)")
    args = parser.parse_args()

    SpecGreedy(args.graph, args.k, args.method)

if __name__ == "__main__":
    main()