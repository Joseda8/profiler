"""
Threaded object/list manipulation benchmark for energy consumption tests.

Creates simple Person instances, duplicates active ones, and builds display
names to stress Python object handling and list operations.
"""

import argparse
import concurrent.futures
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
    people: List[Person] = []
    for index in range(num_records):
        first_name = f"Name{index}"
        last_name = f"Surname{index % 100}"
        age = (index % 80) + 18
        active = index % 2 == 0
        people.append(Person(person_id=index, first_name=first_name, last_name=last_name, age=age, active=active))
    return people


def process_people_slice(start_index: int, end_index: int, people: List[Person]) -> Tuple[int, int]:
    """
    Transform a slice of people:
    - Duplicate active users with an incremented age.
    - Build display names.
    Return counts and a checksum based on name lengths and ages.
    """
    processed: List[Person] = []
    for person in people[start_index:end_index]:
        processed.append(person)
        if person.active:
            duplicated = Person(
                person_id=person.person_id,
                first_name=person.first_name,
                last_name=person.last_name,
                age=person.age + 1,
                active=person.active,
            )
            processed.append(duplicated)

    display_names = [f"{p.first_name} {p.last_name}" for p in processed]
    checksum = sum(len(name) + p.age for name, p in zip(display_names, processed))
    return len(processed), checksum


def run_object_list_benchmark(people: List[Person], num_workers: int) -> int:
    """Run list/object transformations across threads and return a checksum."""
    partial_results: List[Tuple[int, int]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [
            executor.submit(process_people_slice, start_index, end_index, people)
            for start_index, end_index in chunk_indices(len(people), num_workers)
        ]
        for future in concurrent.futures.as_completed(futures):
            partial_results.append(future.result())

    total_processed = sum(count for count, _ in partial_results)
    total_checksum = sum(checksum for _, checksum in partial_results)
    return total_processed + total_checksum


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Object/list manipulation benchmark.")
    parser.add_argument("--num_workers", required=True, type=int, help="Number of worker threads.")
    parser.add_argument("--num_records", type=int, default=50000, help="Number of Person objects to generate.")
    args = parser.parse_args()

    num_workers = args.num_workers
    num_records = args.num_records
    runtime_flavor = runtime_flavor_suffix()

    set_output_filename(filename=f"object_lists_{num_workers}_{num_records}_{runtime_flavor}")

    # Pre-build objects
    people = build_people(num_records)

    set_tag("start_object_lists")
    checksum = run_object_list_benchmark(people=people, num_workers=num_workers)
    set_tag("finish_object_lists")

    print(f"checksum: {checksum}")
