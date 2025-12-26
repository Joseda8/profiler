"""
NumPy BLAS (dot product) benchmark for energy consumption tests.

Computes a matrix multiplication using NumPy/BLAS and returns a checksum.
"""

import argparse
import numpy as np

from src.client_interface import set_output_filename, set_tag
from test_cases.util import runtime_flavor_suffix


def build_matrices(size: int) -> tuple[np.ndarray, np.ndarray]:
    """Create deterministic input matrices."""
    rng = np.random.default_rng(123)
    matrix_a = rng.random((size, size), dtype=np.float64)
    matrix_b = rng.random((size, size), dtype=np.float64)
    return matrix_a, matrix_b


def dot_checksum(matrix_a: np.ndarray, matrix_b: np.ndarray) -> float:
    """Compute matrix product and return a checksum."""
    product = matrix_a.dot(matrix_b)
    return float(product.sum())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NumPy BLAS (dot product) benchmark.")
    parser.add_argument("--size", type=int, default=1000, help="Square matrix size (size x size).")
    args = parser.parse_args()

    size = args.size
    runtime_flavor = runtime_flavor_suffix()

    set_output_filename(filename=f"numpy_blas_{size}_{runtime_flavor}")

    matrix_a, matrix_b = build_matrices(size)

    set_tag("start_numpy_blas")
    checksum = dot_checksum(matrix_a=matrix_a, matrix_b=matrix_b)
    set_tag("finish_numpy_blas")

    print(f"checksum: {checksum}")
