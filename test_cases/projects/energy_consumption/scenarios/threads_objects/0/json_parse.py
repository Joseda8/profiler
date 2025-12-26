"""
Threaded JSON parsing benchmark for energy consumption tests.
"""

import argparse
import concurrent.futures
import json
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


def build_payloads(num_records: int) -> List[str]:
    """
    Generate synthetic JSON payloads (no external data dependency) for parsing.
    """
    payloads: List[str] = []
    for record_index in range(num_records):
        record = {
            "id": record_index,
            "dob": {"age": (record_index % 90) + 10},
            "active": record_index % 3 == 0,
        }
        payloads.append(json.dumps(record))
    return payloads


def parse_slice(start_index: int, end_index: int, payloads: List[str]) -> Tuple[int, int]:
    """
    Parse a slice of JSON payloads and accumulate simple stats.

    We count records and sum ages to keep the workload deterministic.
    """
    record_count = 0
    age_sum = 0
    for payload in payloads[start_index:end_index]:
        record = json.loads(payload)
        record_count += 1
        age_sum += int(record.get("dob", {}).get("age", 0))
    return record_count, age_sum


def run_parse_benchmark(payloads: List[str], num_workers: int) -> int:
    """Parse a shared payload list in parallel and return a checksum."""
    num_records = len(payloads)
    results: List[Tuple[int, int]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [
            executor.submit(parse_slice, start_index, end_index, payloads)
            for start_index, end_index in chunk_indices(num_records, num_workers)
        ]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

    record_total = sum(count for count, _ in results)
    age_total = sum(age for _, age in results)
    return record_total + age_total


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JSON parsing and aggregation benchmark.")
    parser.add_argument("--num_workers", required=True, type=int, help="Number of worker threads.")
    parser.add_argument("--num_records", type=int, default=50000, help="Number of JSON records to parse.")
    args = parser.parse_args()

    num_workers = args.num_workers
    num_records = args.num_records
    runtime_flavor = runtime_flavor_suffix()

    set_output_filename(filename=f"json_parse_{num_workers}_{num_records}_{runtime_flavor}")

    # Pre-build payloads
    payloads = build_payloads(num_records)

    # Profile only the parsing phase.
    set_tag("start_json_parse")
    checksum = run_parse_benchmark(payloads=payloads, num_workers=num_workers)
    set_tag("finish_json_parse")

    print(f"checksum: {checksum}")
