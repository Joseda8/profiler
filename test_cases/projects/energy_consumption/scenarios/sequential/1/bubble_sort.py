"""
Sequential bubble sort benchmark for energy consumption tests.

Generates a deterministic list and performs bubble sort, returning a checksum
to keep the work observable.
"""

import argparse
import time
from typing import List

from src.client_interface import set_output_filename, set_tag
from test_cases.util import runtime_flavor_suffix


def build_numbers(count: int) -> List[int]:
    """Create a deterministic list of integers in descending order."""
    return list(range(count, 0, -1))


def bubble_sort(values: List[int]) -> None:
    """In-place bubble sort implementation."""
    n = len(values)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if values[j] > values[j + 1]:
                values[j], values[j + 1] = values[j + 1], values[j]
                swapped = True
        if not swapped:
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sequential bubble sort benchmark.")
    parser.add_argument("--num_items", type=int, default=20000, help="Number of items to sort.")
    parser.add_argument("--run_idx", help="Optional run index to tag outputs.")
    args = parser.parse_args()

    num_items = args.num_items
    runtime_flavor = runtime_flavor_suffix()
    run_suffix = f"run{args.run_idx}" if args.run_idx else ""
    set_output_filename(filename=f"bubble_sort_{num_items}_{runtime_flavor}_{run_suffix}")

    # Pre-build input before profiling to focus on sort work
    numbers = build_numbers(num_items)
    time.sleep(3)

    set_tag("start_bubble_sort")
    bubble_sort(numbers)
    set_tag("finish_bubble_sort")
