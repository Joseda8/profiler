"""
Threaded JSON parsing benchmark for energy consumption tests.

Benchmark Steps:
1. Build synthetic JSON payloads.
2. Sleep briefly to isolate setup.
3. Parse payload slices across a thread pool.
"""

import argparse
import concurrent.futures
import json
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


def build_payloads(num_records: int) -> List[str]:
    """
    Generate synthetic JSON payloads for parsing.
    """
    # Local binding
    dumps = json.dumps
    return [
        dumps(
            {
                "id": idx,
                "dob": {"age": (idx % 90) + 10},
                "active": (idx % 3) == 0,
                "scores": {"math": (idx % 50) / 10, "lang": (idx % 40) / 10},
                "tags": [f"tag{idx % 5}", f"group{idx % 7}"],
                "meta": {"source": "synthetic", "epoch": idx // 1000},
            }
        )
        for idx in range(num_records)
    ]


def parse_slice(start_index: int, end_index: int, payloads: List[str]) -> None:
    """
    Parse a slice of JSON payloads and exercise dict-heavy access/mutation:
    - nested reads for ages/scores/tags
    - dict merges and updates
    - JSON round-trips on derived dicts
    """
    age_buckets: dict[int, int] = {}
    for payload in payloads[start_index:end_index]:
        record = json.loads(payload)
        age = int(record.get("dob", {}).get("age", 0))
        tags = record.get("tags", [])
        scores = record.get("scores", {})
        meta = record.get("meta", {}).copy()

        meta["age_bucket"] = age // 10
        meta["tag_count"] = len(tags)
        age_buckets[meta["age_bucket"]] = age_buckets.get(meta["age_bucket"], 0) + 1

        merged = {**scores, "age": age, "active": record.get("active", False), **meta}
        merged.setdefault("checksum", record["id"] ^ age)

        # Round-trip derived dict to JSON to stress encode/decode paths
        json.loads(json.dumps(merged))
    return


def run_parse_benchmark(payloads: List[str], num_workers: int) -> None:
    """Parse a shared payload list in parallel."""
    num_records = len(payloads)
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [
            executor.submit(parse_slice, start_index, end_index, payloads)
            for start_index, end_index in chunk_indices(num_records, num_workers)
        ]
        for future in concurrent.futures.as_completed(futures):
            future.result()

    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JSON parsing benchmark.")
    parser.add_argument("--num_workers", required=True, type=int, help="Number of worker threads.")
    parser.add_argument("--num_records", type=int, default=50000, help="Number of JSON records to parse.")
    parser.add_argument("--run_idx", help="Optional run index to tag outputs.")
    args = parser.parse_args()

    num_workers = args.num_workers
    num_records = args.num_records
    runtime_flavor = runtime_flavor_suffix()
    run_suffix = f"run{args.run_idx}" if args.run_idx else ""

    set_output_filename(filename=f"json_parse_{num_workers}_{num_records}_{runtime_flavor}_{run_suffix}")

    # Pre-build payloads
    payloads = build_payloads(num_records)
    time.sleep(3)

    # Profile only the parsing phase.
    set_tag("start_json_parse")
    run_parse_benchmark(payloads=payloads, num_workers=num_workers)
    set_tag("finish_json_parse")
