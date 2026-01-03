"""
NumPy FFT benchmark for energy consumption tests.

Computes a 1D FFT on a prebuilt array.
"""

import argparse
import time
import numpy as np

from src.client_interface import set_output_filename, set_tag
from test_cases.util import runtime_flavor_suffix


def build_signal(length: int) -> np.ndarray:
    """Create a deterministic input signal."""
    rng = np.random.default_rng(123)
    return rng.standard_normal(length, dtype=np.float64)


def run_fft(signal: np.ndarray) -> None:
    """Compute FFT."""
    spectrum = np.fft.fft(signal)
    np.abs(spectrum).sum()
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NumPy FFT benchmark.")
    parser.add_argument("--length", type=int, default=1_000_000, help="Length of the signal.")
    parser.add_argument("--run_idx", help="Optional run index to tag outputs.")
    args = parser.parse_args()

    length = args.length
    runtime_flavor = runtime_flavor_suffix()
    run_suffix = f"run{args.run_idx}" if args.run_idx else ""
    set_output_filename(filename=f"numpy_fft_{length}_{runtime_flavor}_{run_suffix}")

    # Pre-build data
    signal = build_signal(length)
    time.sleep(3)

    set_tag("start_numpy_fft")
    run_fft(signal)
    set_tag("finish_numpy_fft")
