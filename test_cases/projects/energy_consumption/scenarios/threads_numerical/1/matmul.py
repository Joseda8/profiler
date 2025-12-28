"""
Threaded matrix multiplication benchmark for energy consumption tests.
"""

import argparse
import concurrent.futures
from typing import Iterable, List

from src.client_interface import set_output_filename, set_tag
from test_cases.util import runtime_flavor_suffix


def build_matrix(size: int) -> List[List[int]]:
    """Create a square matrix (size x size) with deterministic integer values."""
    return [[(row_index + column_index) % 100 for column_index in range(size)] for row_index in range(size)]


def transpose(square_matrix: List[List[int]]) -> List[List[int]]:
    """Transpose a square matrix."""
    matrix_size = len(square_matrix)
    return [[square_matrix[row_index][column_index] for row_index in range(matrix_size)] for column_index in range(matrix_size)]


def compute_checksum_for_row_slice(
    start_row_index: int,
    end_row_index: int,
    left_matrix: List[List[int]],
    right_matrix_transposed: List[List[int]],
) -> int:
    """
    Multiply the specified slice of rows of the left matrix by the right matrix (already transposed)
    and return the checksum of all resulting cells.
    """
    checksum = 0
    for row_index in range(start_row_index, end_row_index):
        row_values = left_matrix[row_index]
        for column_values in right_matrix_transposed:
            cell_value = sum(left_value * right_value for left_value, right_value in zip(row_values, column_values))
            checksum += cell_value
    return checksum


def chunk_indices(total_rows: int, num_workers: int) -> Iterable[tuple[int, int]]:
    """Yield (start, end) index pairs that partition the total rows across the workers."""
    rows_per_worker = (total_rows + num_workers - 1) // num_workers
    for worker_index in range(num_workers):
        start_index = worker_index * rows_per_worker
        end_index = min(start_index + rows_per_worker, total_rows)
        if start_index >= total_rows:
            break
        yield start_index, end_index


def run_matmul_benchmark(matrix_size: int, num_workers: int) -> int:
    """Compute matrix multiplication checksum using a thread pool."""
    left_matrix = build_matrix(matrix_size)
    right_matrix_transposed = transpose(build_matrix(matrix_size))

    total_checksum = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        future_checksums = [
            executor.submit(
                compute_checksum_for_row_slice,
                start_row_index,
                end_row_index,
                left_matrix,
                right_matrix_transposed,
            )
            for start_row_index, end_row_index in chunk_indices(matrix_size, num_workers)
        ]
        for future in concurrent.futures.as_completed(future_checksums):
            total_checksum += future.result()
    return total_checksum


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parallel matrix multiplication benchmark.")
    parser.add_argument("--num_workers", required=True, type=int, help="Number of worker threads.")
    parser.add_argument("--matrix_size", type=int, default=256, help="Square matrix size (size x size).")
    parser.add_argument("--run_idx", help="Optional run index to tag outputs.")
    args = parser.parse_args()

    num_workers = args.num_workers
    matrix_size = args.matrix_size
    runtime_flavor = runtime_flavor_suffix()
    run_suffix = f"run{args.run_idx}" if args.run_idx else ""

    set_output_filename(filename=f"matmul_{num_workers}_{matrix_size}_{runtime_flavor}_{run_suffix}")

    set_tag("start_matmul")
    checksum = run_matmul_benchmark(matrix_size=matrix_size, num_workers=num_workers)
    set_tag("finish_matmul")

    print(f"checksum: {checksum}")
