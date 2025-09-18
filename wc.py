#!/usr/bin/env -S uv run --script

from parallelism import pmap
import random
import hashlib

def count_words(text_chunk):
    """Count words in a chunk of text"""
    counts = {}
    for word in text_chunk:
        hashlib.md5(word.encode()).hexdigest()
        counts[word] = counts.get(word, 0) + 1
    return counts

def merge_counts(count_dicts):
    """Merge multiple count dictionaries"""
    result = {}
    for d in count_dicts:
        for word, count in d.items():
            result[word] = result.get(word, 0) + count
    return result

if __name__ == "__main__":
    # Generate much larger test data to saturate 12 cores for minutes
    words = ["hello", "world", "python", "parallel", "cpu", "cores", "thread", "process",
             "data", "algorithm", "benchmark", "performance", "memory", "cache", "loop",
             "function", "variable", "string", "integer", "float", "boolean", "array"]

    print("Generating large dataset...")
    text = [random.choice(words) for _ in range(100_000_000)]  # 100M words

    print(f"Processing {len(text):,} words across all CPU cores...")

    # Split into smaller chunks to maximize parallelism
    chunk_size = 50_000  # Smaller chunks = better load distribution
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    print(f"Split into {len(chunks)} chunks of {chunk_size} words each")

    # Use pmap to count words in parallel - this will saturate all CPU cores
    word_counts = pmap(count_words, chunks)

    # Merge results
    final_counts = merge_counts(word_counts)

    # Print results
    for word, count in sorted(final_counts.items()):
        print(f"{word}: {count}")
