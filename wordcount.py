#!/usr/bin/env -S uv run --script
"""
Word count benchmark - tokenize & count words with dict/list ops.
"""
import random


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


if __name__ == "__main__":
    size = 100_000_000
    fn = bench_wordcount(size)
    result = fn()
    print(f"Most common word: {result}")
