"""
NumPy vectorized benchmark for energy consumption tests.

Performs chained vectorized operations on prebuilt arrays to compare GIL vs
native-extension performance.
"""

import argparse
import numpy as np

from src.client_interface import set_output_filename, set_tag
from test_cases.util import runtime_flavor_suffix


def build_arrays(length: int) -> tuple[np.ndarray, np.ndarray]:
    """Create deterministic input arrays."""
    rng = np.random.default_rng(42)
    array_a = rng.random(length, dtype=np.float64)
    array_b = rng.random(length, dtype=np.float64)
    return array_a, array_b


def vectorized_work(array_a: np.ndarray, array_b: np.ndarray) -> float:
    """Run chained vectorized ops and return a checksum."""
    combined = array_a * array_b + array_a * 0.5 - array_b * 0.25
    clipped = np.clip(combined, 0.0, 1.0)
    normalized = (clipped - clipped.mean()) / (clipped.std() + 1e-9)
    return float(np.sum(normalized))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NumPy vectorized benchmark.")
    parser.add_argument("--length", type=int, default=5_000_000, help="Length of input arrays.")
    parser.add_argument("--run_idx", help="Optional run index to tag outputs.")
    args = parser.parse_args()

    length = args.length
    runtime_flavor = runtime_flavor_suffix()
    run_suffix = f"run{args.run_idx}" if args.run_idx else ""

    set_output_filename(filename=f"numpy_vectorized_{length}_{runtime_flavor}_{run_suffix}")

    array_a, array_b = build_arrays(length)

    set_tag("start_numpy_vectorized")
    checksum = vectorized_work(array_a=array_a, array_b=array_b)
    set_tag("finish_numpy_vectorized")

    print(f"checksum: {checksum}")
