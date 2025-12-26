"""
Threaded text tokenization benchmark for energy consumption tests.
"""

import argparse
import concurrent.futures
from collections import Counter
from typing import Iterable, List, Tuple

from src.client_interface import set_output_filename, set_tag
from test_cases.util import runtime_flavor_suffix


def chunk_indices(total_items: int, num_workers: int) -> Iterable[Tuple[int, int]]:
    """Yield (start, end) index pairs that partition the items across workers."""
    items_per_worker = (total_items + num_workers - 1) // num_workers
    for worker_index in range(num_workers):
        start_index = worker_index * items_per_worker
        end_index = min(start_index + items_per_worker, total_items)
        if start_index >= total_items:
            break
        yield start_index, end_index


def build_sentences(num_records: int) -> List[str]:
    """Generate synthetic sentences for tokenization."""
    base_sentences = [
        "Concurrency without a global interpreter lock enables true parallelism.",
        "Thread scheduling affects throughput and latency.",
        "Text processing stresses object allocation and reference counting.",
        "Deterministic workloads help compare runtimes fairly.",
    ]
    sentences: List[str] = []
    for index in range(num_records):
        template = base_sentences[index % len(base_sentences)]
        sentences.append(f"{template} record-{index}")
    return sentences


def tokenize_slice(start_index: int, end_index: int, sentences: List[str]) -> Counter:
    """Tokenize a slice of sentences and return token frequency counts."""
    token_counts: Counter = Counter()
    for sentence in sentences[start_index:end_index]:
        tokens = sentence.lower().split()
        token_counts.update(tokens)
    return token_counts


def run_tokenize_benchmark(sentences: List[str], num_workers: int) -> int:
    """Tokenize all sentences using a thread pool and return the total token count."""
    counters: List[Counter] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [
            executor.submit(tokenize_slice, start_index, end_index, sentences)
            for start_index, end_index in chunk_indices(len(sentences), num_workers)
        ]
        for future in concurrent.futures.as_completed(futures):
            counters.append(future.result())

    merged = Counter()
    for counter in counters:
        merged.update(counter)

    return sum(merged.values())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Text tokenization benchmark.")
    parser.add_argument("--num_workers", required=True, type=int, help="Number of worker threads.")
    parser.add_argument("--num_records", type=int, default=50000, help="Number of text records to tokenize.")
    args = parser.parse_args()

    num_workers = args.num_workers
    num_records = args.num_records
    runtime_flavor = runtime_flavor_suffix()

    set_output_filename(filename=f"text_tokenize_{num_workers}_{num_records}_{runtime_flavor}")

    # Pre-build sentences; profiling should focus on tokenization, not data generation.
    sentences = build_sentences(num_records)

    set_tag("start_text_tokenize")
    checksum = run_tokenize_benchmark(sentences=sentences, num_workers=num_workers)
    set_tag("finish_text_tokenize")

    print(f"checksum: {checksum}")
