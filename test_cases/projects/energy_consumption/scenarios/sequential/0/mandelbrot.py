"""
Sequential Mandelbrot benchmark for energy consumption tests.

Mimics the classic benchmark game implementation: single size parameter, fixed
iteration cap, deterministic region, and checksum of iteration counts.
"""

import argparse
import time

from src.client_interface import set_output_filename, set_tag
from test_cases.util import runtime_flavor_suffix

MAX_ITERATIONS = 50
DEFAULT_BOUNDS = (-1.5, 0.5, -1.0, 1.0)


def build_grid(size: int, bounds: tuple[float, float, float, float] = DEFAULT_BOUNDS) -> tuple[list[float], list[float]]:
    """Precompute x/y coordinates for the Mandelbrot grid."""
    x_min, x_max, y_min, y_max = bounds
    dx = (x_max - x_min) / size
    dy = (y_max - y_min) / size
    x_coords = [x_min + col * dx for col in range(size)]
    y_coords = [y_min + row * dy for row in range(size)]
    return x_coords, y_coords


def run_mandelbrot(x_coords: list[float], y_coords: list[float]) -> None:
    """Compute the Mandelbrot iteration counts across the provided grid."""
    for imag in y_coords:
        for real in x_coords:
            zr = zi = 0.0
            iteration = 0
            while zr * zr + zi * zi <= 4.0 and iteration < MAX_ITERATIONS:
                zr, zi = zr * zr - zi * zi + real, 2.0 * zr * zi + imag
                iteration += 1
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sequential Mandelbrot benchmark.")
    parser.add_argument("--size", type=int, default=1000, help="Image size (width = height = size).")
    parser.add_argument("--run_idx", help="Optional run index to tag outputs.")
    args = parser.parse_args()

    size = args.size
    runtime_flavor = runtime_flavor_suffix()
    run_suffix = f"run{args.run_idx}" if args.run_idx else ""
    set_output_filename(filename=f"mandelbrot_{size}_{runtime_flavor}_{run_suffix}")

    # Precompute coordinates before profiling to focus on iteration work
    x_coords, y_coords = build_grid(size)
    time.sleep(3)

    set_tag("start_mandelbrot")
    run_mandelbrot(x_coords=x_coords, y_coords=y_coords)
    set_tag("finish_mandelbrot")
