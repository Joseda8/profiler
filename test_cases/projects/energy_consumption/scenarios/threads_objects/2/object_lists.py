"""
Threaded object/list manipulation benchmark for energy consumption tests.

Creates simple Person instances, duplicates active ones, and builds display
names to stress Python object handling and list operations.
"""

import argparse
import concurrent.futures
import time
from dataclasses import dataclass
from typing import Iterable, List, Tuple

from src.client_interface import set_output_filename, set_tag
from test_cases.util import runtime_flavor_suffix

@dataclass
class Person:
    """Minimal person model used for list-heavy operations."""

    person_id: int
    first_name: str
    last_name: str
    age: int
    active: bool


def chunk_indices(total_items: int, num_workers: int) -> Iterable[Tuple[int, int]]:
    """Yield (start, end) index pairs that partition the items across workers."""
    items_per_worker = (total_items + num_workers - 1) // num_workers
    for worker_index in range(num_workers):
        start_index = worker_index * items_per_worker
        end_index = min(start_index + items_per_worker, total_items)
        if start_index >= total_items:
            break
        yield start_index, end_index


def build_people(num_records: int) -> List[Person]:
    """Generate a deterministic list of Person instances."""
    # Local binding
    Person_ = Person
    return [
        Person_(
            idx,
            f"Name{idx}",
            f"Surname{idx}",
            idx % 80,
            (idx & 1) == 0,
        )
        for idx in range(num_records)
    ]


def process_people_slice(start_index: int, end_index: int, people: List[Person]) -> None:
    """
    Transform a slice of people:
    - Duplicate active users with an incremented age.
    - Build display names.
    - Apply extra list churn (copies, concatenations, slice merges) to stress list behavior.
    """
    # Collect original and duplicated records for this slice
    processed: List[Person] = []
    for person in people[start_index:end_index]:
        processed.append(person)
        if person.active:
            # Duplicate actives with slight modification to force list growth
            duplicated = Person(
                person_id=person.person_id,
                first_name=person.first_name,
                last_name=person.last_name,
                age=person.age + 1,
                active=person.active,
            )
            processed.append(duplicated)

    # List-heavy operations
    # Build a separate list of names to copy via list comprehension
    names = [f"{p.first_name} {p.last_name}" for p in processed]

    # Concatenate list with its first half
    processed = processed + processed[: len(processed) // 2]

    # Rebuild list by merging even/odd slices (copy + concat)
    processed = processed[::2] + processed[1::2]

    # In-place slice assignment to exercise mutation
    processed[: len(names)] = processed[: len(names)]

    return


def run_object_list_benchmark(people: List[Person], num_workers: int) -> None:
    """Run list/object transformations across threads."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [
            executor.submit(process_people_slice, start_index, end_index, people)
            for start_index, end_index in chunk_indices(len(people), num_workers)
        ]
        for future in concurrent.futures.as_completed(futures):
            future.result()

    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Object/list manipulation benchmark.")
    parser.add_argument("--num_workers", required=True, type=int, help="Number of worker threads.")
    parser.add_argument("--num_records", type=int, default=50000, help="Number of Person objects to generate.")
    parser.add_argument("--run_idx", help="Optional run index to tag outputs.")
    args = parser.parse_args()

    num_workers = args.num_workers
    num_records = args.num_records
    runtime_flavor = runtime_flavor_suffix()
    run_suffix = f"run{args.run_idx}" if args.run_idx else ""

    set_output_filename(filename=f"object_lists_{num_workers}_{num_records}_{runtime_flavor}_{run_suffix}")

    # Pre-build objects
    people = build_people(num_records)
    time.sleep(3)

    set_tag("start_object_lists")
    run_object_list_benchmark(people=people, num_workers=num_workers)
    set_tag("finish_object_lists")
