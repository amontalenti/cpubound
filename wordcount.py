#!/usr/bin/env -S uv run --script
"""
Word count benchmark - tokenize & count words with dict/list ops.
"""
import random
from parallelism import pmap


def count_words_chunk(words):
    counts = {}
    for w in words:
        counts[w] = counts.get(w, 0) + 1
    return counts


def reduce_counts(count_dicts):
    merged = {}
    for count_dict in count_dicts:
        for word, count in count_dict.items():
            merged[word] = merged.get(word, 0) + count
    return merged


def bench_wordcount(size):
    # size ~ number of tokens
    n = max(200_000, int(size))
    random.seed(99)
    vocab = ["lorem", "ipsum", "dolor", "sit", "amet", "consectetur",
             "adipiscing", "elit", "sed", "do", "eiusmod", "tempor"]
    text = [random.choice(vocab) for _ in range(n)]

    def run():
        # Split text into chunks for parallel processing
        chunk_size = max(1, len(text) // 16)  # Create 16 chunks
        chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

        # Use pmap to count words in parallel chunks
        chunk_counts = pmap(count_words_chunk, chunks, num_workers=16)

        # Reduce step: merge all count dictionaries
        final_counts = reduce_counts(chunk_counts)

        # return the most common word
        return max(final_counts.items(), key=lambda kv: kv[1])[0]
    return run


if __name__ == "__main__":
    size = 100_000_000
    fn = bench_wordcount(size)
    result = fn()
    print(f"Most common word: {result}")
