"""
Threaded factorial benchmark for energy consumption tests.
"""

import argparse
import concurrent.futures
import math
from typing import Iterable

from src.client_interface import set_tag, set_output_filename
from test_cases.util import runtime_flavor_suffix


def factorial(value: int) -> int:
    """Compute factorial of the provided integer."""
    return math.factorial(value)


def run_factorial_benchmark(factorial_inputs: Iterable[int], num_workers: int) -> None:
    """Compute all factorials using a thread pool, ignoring individual results."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        future_to_input = {executor.submit(factorial, value): value for value in factorial_inputs}
        for future in concurrent.futures.as_completed(future_to_input):
            future.result()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute factorials using a thread pool.")
    parser.add_argument("--num_workers", required=True, type=int, help="Number of worker threads.")
    args = parser.parse_args()

    num_workers = args.num_workers
    runtime_flavor = runtime_flavor_suffix()
    factorial_inputs = list(range(10000))

    set_output_filename(filename=f"factorial_{num_workers}_{runtime_flavor}")
    set_tag("start_factorial")
    run_factorial_benchmark(factorial_inputs=factorial_inputs, num_workers=num_workers)
    set_tag("finish_factorial")
