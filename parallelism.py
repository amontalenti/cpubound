from concurrent.futures import ThreadPoolExecutor
import itertools

def pmap(func, iterable, max_workers=None, chunk_size=None):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        items = list(iterable)

        if chunk_size is None:
            # Auto-partition based on number of workers
            num_workers = executor._max_workers
            chunk_size = max(1, len(items) // (num_workers * 4))

        # Partition into chunks
        chunks = [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]

        # Process chunks in parallel
        def process_chunk(chunk):
            return [func(item) for item in chunk]

        chunk_results = list(executor.map(process_chunk, chunks))

        # Flatten results
        return [item for chunk in chunk_results for item in chunk]