"""
Threaded shared-list mutation benchmark for energy consumption tests.

Benchmark Steps:
1. Build a deterministic list of strings.
2. Sleep briefly to isolate setup.
3. Mutate disjoint slices in place across threads (uppercase).
"""

import argparse
import concurrent.futures
import time
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


def build_strings(num_records: int) -> List[str]:
    """
    Generate a deterministic list of string records.

    Threads will mutate this shared list in place.
    """
    return [f"name{idx} middleName{idx} surname{idx}" for idx in range(num_records)]


def process_slice_in_place(start_index: int, end_index: int, records: List[str]) -> None:
    """
    Mutate a shared list slice in place:
    - Uppercase every string in the assigned slice.
    - Reassign back to the shared list (no copies for the base slice).
    """
    for idx in range(start_index, end_index):
        original = records[idx]
        records[idx] = original.upper()

    return


def run_object_list_benchmark(records: List[str], num_workers: int) -> None:
    """Run in-place string uppercasing across threads over disjoint slices."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [
            executor.submit(process_slice_in_place, start_index, end_index, records)
            for start_index, end_index in chunk_indices(len(records), num_workers)
        ]
        for future in concurrent.futures.as_completed(futures):
            future.result()

    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Shared-list mutation benchmark (threaded uppercasing).")
    parser.add_argument("--num_workers", required=True, type=int, help="Number of worker threads.")
    parser.add_argument("--num_records", type=int, default=50000, help="Number of string records to generate.")
    parser.add_argument("--run_idx", help="Optional run index to tag outputs.")
    args = parser.parse_args()

    num_workers = args.num_workers
    num_records = args.num_records
    runtime_flavor = runtime_flavor_suffix()
    run_suffix = f"run{args.run_idx}" if args.run_idx else ""

    set_output_filename(filename=f"object_lists_nocopy_{num_workers}_{num_records}_{runtime_flavor}_{run_suffix}")

    # Pre-build shared string list to mutate in place
    records = build_strings(num_records)
    time.sleep(3)

    set_tag("start_object_lists")
    run_object_list_benchmark(records=records, num_workers=num_workers)
    set_tag("finish_object_lists")
