"""
NumPy BLAS (dot product) benchmark for energy consumption tests.

Benchmark Steps:
1. Build deterministic square matrices.
2. Sleep briefly to isolate setup.
3. Multiply matrices and reduce to keep work materialized.
"""

import argparse
import time
import numpy as np

from src.client_interface import set_output_filename, set_tag
from test_cases.util import runtime_flavor_suffix


def build_matrices(size: int) -> tuple[np.ndarray, np.ndarray]:
    """Create deterministic input matrices."""
    rng = np.random.default_rng(123)
    matrix_a = rng.random((size, size), dtype=np.float64)
    matrix_b = rng.random((size, size), dtype=np.float64)
    return matrix_a, matrix_b


def run_blas_dot(matrix_a: np.ndarray, matrix_b: np.ndarray) -> None:
    """Compute matrix product and force a reduction to keep work materialized."""
    product = matrix_a.dot(matrix_b)
    product.sum()
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NumPy BLAS (dot product) benchmark.")
    parser.add_argument("--size", type=int, default=1000, help="Square matrix size (size x size).")
    parser.add_argument("--run_idx", help="Optional run index to tag outputs.")
    args = parser.parse_args()

    size = args.size
    runtime_flavor = runtime_flavor_suffix()
    run_suffix = f"run{args.run_idx}" if args.run_idx else ""
    set_output_filename(filename=f"numpy_blas_{size}_{runtime_flavor}_{run_suffix}")

    # Pre-build data before profiling to keep measurements focused on BLAS
    matrix_a, matrix_b = build_matrices(size)
    time.sleep(3)

    set_tag("start_numpy_blas")
    run_blas_dot(matrix_a=matrix_a, matrix_b=matrix_b)
    set_tag("finish_numpy_blas")
