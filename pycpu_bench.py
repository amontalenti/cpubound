#!/usr/bin/env python3
"""
Pure-Python CPU-bound microbenchmarks (no NumPy, no C-extensions).

Workloads:
  - binary_trees: build/traverse binary trees (object allocation + recursion)
  - matrix_multiply: naive triple-loop multiplication of Python lists
  - levenshtein: edit distance DP over lists
  - sieve_primes: simple sieve using Python lists/booleans
  - topo_sort: DFS-based topological sort over a random DAG
  - wordcount: tokenize & count words with dict/list ops

Usage:
  python pycpu_bench.py --bench all --size M --repeat R

Sizes are *rough*; increase to stress CPU (and Python interpreter overhead).
"""
import argparse, random, string, time
from collections import defaultdict, deque

# ---------------------------
# Utilities
# ---------------------------
def timer(fn, repeat=3, warmup=1):
    for _ in range(warmup):
        fn()
    ts = []
    for _ in range(repeat):
        t0 = time.perf_counter()
        fn()
        ts.append(time.perf_counter() - t0)
    return min(ts), sum(ts)/len(ts), max(ts)

def report(name, size, times):
    tmin, tavg, tmax = times
    print(f"{name:<16} size={size:<8} min={tmin:.4f}s avg={tavg:.4f}s max={tmax:.4f}s")

# ---------------------------
# Benchmarks
# ---------------------------
class Node:
    __slots__ = ("left","right","val")
    def __init__(self, left=None, right=None, val=1):
        self.left = left
        self.right = right
        self.val = val

def build_tree(depth):
    if depth == 0:
        return Node()
    return Node(build_tree(depth-1), build_tree(depth-1), 1)

def tree_checksum(n: Node) -> int:
    # XOR checksum to force traversal work
    s = 0
    stack = [n]
    while stack:
        cur = stack.pop()
        s ^= cur.val
        if cur.left: stack.append(cur.left)
        if cur.right: stack.append(cur.right)
    return s

def bench_binary_trees(size):
    # size ~ depth
    depth = max(4, int(size))
    def run():
        root = build_tree(depth)
        return tree_checksum(root)
    return run

def bench_matrix_multiply(size):
    # size ~ N for NxN matrices
    n = max(32, int(size))
    random.seed(42)
    A = [[(i*j + 1) % 97 for j in range(n)] for i in range(n)]
    B = [[(i + j + 3) % 89 for j in range(n)] for i in range(n)]
    # Pre-transpose B for cache-friendly row access in Python lists
    BT = list(map(list, zip(*B)))
    def run():
        C = [[0]*n for _ in range(n)]
        for i in range(n):
            Ai = A[i]
            Ci = C[i]
            for j in range(n):
                s = 0
                BTj = BT[j]
                for k in range(n):
                    s += Ai[k] * BTj[k]
                Ci[j] = s
        return C[-1][-1]
    return run

def bench_levenshtein(size):
    # size ~ length of strings
    m = n = max(200, int(size))
    random.seed(123)
    alphabet = string.ascii_lowercase
    s = ''.join(random.choice(alphabet) for _ in range(m))
    t = ''.join(random.choice(alphabet) for _ in range(n))
    def run():
        # classic DP over two rows (lists)
        prev = list(range(n+1))
        for i in range(1, m+1):
            cur = [i] + [0]*n
            si = s[i-1]
            for j in range(1, n+1):
                cost = 0 if si == t[j-1] else 1
                cur[j] = min(
                    prev[j] + 1,      # deletion
                    cur[j-1] + 1,     # insertion
                    prev[j-1] + cost  # substitution
                )
            prev = cur
        return prev[n]
    return run

def bench_sieve_primes(size):
    # size ~ upper bound N
    N = max(100_000, int(size))
    def run():
        sieve = [True] * (N+1)
        sieve[0] = sieve[1] = False
        p = 2
        while p * p <= N:
            if sieve[p]:
                step = p
                start = p*p
                sieve[start:N+1:step] = [False]*(((N - start)//step) + 1)
            p += 1
        return sum(1 for i, v in enumerate(sieve) if v and i <= N)
    return run

def bench_topo_sort(size):
    # size ~ number of nodes
    n = max(5_000, int(size))
    random.seed(7)
    # Build a sparse DAG with edges from i -> j for i<j with low probability
    edges = [[] for _ in range(n)]
    for i in range(n):
        # average ~ 3 outgoing edges
        for _ in range(3):
            j = random.randint(i, n-1)
            if j > i:
                edges[i].append(j)

    def run():
        # DFS-based topo sort
        visited = [0]*n  # 0=unseen,1=visiting,2=done
        out = []

        def dfs(u):
            if visited[u] == 1: raise ValueError("cycle")
            if visited[u] == 2: return
            visited[u] = 1
            for v in edges[u]:
                dfs(v)
            visited[u] = 2
            out.append(u)

        for u in range(n):
            if visited[u] == 0:
                dfs(u)
        return out[-1]
    return run

def bench_wordcount(size):
    # size ~ number of tokens
    n = max(200_000, int(size))
    random.seed(99)
    vocab = ["lorem", "ipsum", "dolor", "sit", "amet", "consectetur",
             "adipiscing", "elit", "sed", "do", "eiusmod", "tempor"]
    text = [random.choice(vocab) for _ in range(n)]
    def run():
        counts = {}
        for w in text:
            counts[w] = counts.get(w, 0) + 1
        # return the most common word
        return max(counts.items(), key=lambda kv: kv[1])[0]
    return run

BENCHES = {
    "binary_trees": bench_binary_trees,
    "matrix_multiply": bench_matrix_multiply,
    "levenshtein": bench_levenshtein,
    "sieve_primes": bench_sieve_primes,
    "topo_sort": bench_topo_sort,
    "wordcount": bench_wordcount,
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bench", default="none", choices=list(BENCHES.keys())+["all"])
    parser.add_argument("--size", type=int, default=100_000_000)
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--warmup", type=int, default=1)
    args = parser.parse_args()

    if args.bench not in BENCHES:
        print(f"Select a bench from {list(BENCHES.keys())} and pass via --bench")
        return

    benches = BENCHES.items() if args.bench == "all" else [(args.bench, BENCHES[args.bench])]
    for name, factory in benches:
        fn = factory(args.size)
        times = timer(fn, repeat=args.repeat, warmup=args.warmup)
        report(name, args.size, times)

if __name__ == "__main__":
    main()
