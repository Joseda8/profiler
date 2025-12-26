import argparse
import concurrent.futures
import hashlib
from typing import Iterable, List, Tuple

from src.client_interface import set_output_filename, set_tag
from test_cases.util import runtime_flavor_suffix


def chunk_indices(total_items: int, num_workers: int) -> Iterable[Tuple[int, int]]:
    items_per_worker = (total_items + num_workers - 1) // num_workers
    for worker_index in range(num_workers):
        start_index = worker_index * items_per_worker
        end_index = min(start_index + items_per_worker, total_items)
        if start_index >= total_items:
            break
        yield start_index, end_index


def build_records(num_records: int) -> List[str]:
    base_values = [
        "alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta", "iota", "kappa",
    ]
    records = []
    for index in range(num_records):
        prefix = base_values[index % len(base_values)]
        records.append(f"{prefix}-record-{index}-payload-for-hash")
    return records


def hash_slice(start_index: int, end_index: int, records: List[str]) -> int:
    checksum = 0
    for record in records[start_index:end_index]:
        digest = hashlib.sha256(record.encode("utf-8")).digest()
        checksum += int.from_bytes(digest[:8], byteorder="big", signed=False)
    return checksum


def run_hash_benchmark(records: List[str], num_workers: int) -> int:
    partial_checksums: List[int] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [
            executor.submit(hash_slice, start_index, end_index, records)
            for start_index, end_index in chunk_indices(len(records), num_workers)
        ]
        for future in concurrent.futures.as_completed(futures):
            partial_checksums.append(future.result())

    return sum(partial_checksums)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Record hashing benchmark.")
    parser.add_argument("--num_workers", required=True, type=int, help="Number of worker threads.")
    parser.add_argument("--num_records", type=int, default=50000, help="Number of records to hash.")
    args = parser.parse_args()

    num_workers = args.num_workers
    num_records = args.num_records
    runtime_flavor = runtime_flavor_suffix()

    set_output_filename(filename=f"hash_records_{num_workers}_{num_records}_{runtime_flavor}")

    # Pre-build records; profiling should focus on hashing, not data generation.
    records = build_records(num_records)

    set_tag("start_hash_records")
    checksum = run_hash_benchmark(records=records, num_workers=num_workers)
    set_tag("finish_hash_records")

    print(f"checksum: {checksum}")
