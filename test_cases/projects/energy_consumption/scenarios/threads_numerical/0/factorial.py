import argparse
import concurrent.futures
import math

from src.client_interface import set_tag, set_output_filename
from test_cases.util import runtime_flavor_suffix


def factorial(n: int) -> int:
    """Compute factorial of n."""
    return math.factorial(n)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute factorials using a thread pool.")
    parser.add_argument("--num_workers", required=True, type=int, help="Number of worker threads.")
    args = parser.parse_args()
    num_workers = args.num_workers
    runtime_flavor = runtime_flavor_suffix()

    set_output_filename(filename=f"factorial_{num_workers}_{runtime_flavor}")

    numbers = list(range(10000))

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        set_tag("start_factorial")
        future_to_task = {executor.submit(factorial, num): num for num in numbers}
        for future in concurrent.futures.as_completed(future_to_task):
            try:
                future.result()
            except Exception as exc:
                print(f"An exception occurred: {exc}")
        set_tag("finish_factorial")
