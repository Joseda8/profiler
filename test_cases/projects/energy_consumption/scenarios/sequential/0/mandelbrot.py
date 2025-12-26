"""
Sequential Mandelbrot benchmark for energy consumption tests.

Mimics the classic benchmark game implementation: single size parameter, fixed
iteration cap, deterministic region, and checksum of iteration counts.
"""

import argparse

from src.client_interface import set_output_filename, set_tag
from test_cases.util import runtime_flavor_suffix

MAX_ITERATIONS = 50


def mandelbrot_checksum(size: int) -> int:
    """Compute the Mandelbrot set for an (size x size) grid and return a checksum."""
    x_min, x_max = -1.5, 0.5
    y_min, y_max = -1.0, 1.0
    dx = (x_max - x_min) / size
    dy = (y_max - y_min) / size

    checksum = 0
    for row in range(size):
        imag = y_min + row * dy
        for col in range(size):
            real = x_min + col * dx
            zr = zi = 0.0
            iteration = 0
            while zr * zr + zi * zi <= 4.0 and iteration < MAX_ITERATIONS:
                zr, zi = zr * zr - zi * zi + real, 2.0 * zr * zi + imag
                iteration += 1
            checksum += iteration
    return checksum


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sequential Mandelbrot benchmark.")
    parser.add_argument("--size", type=int, default=1000, help="Image size (width = height = size).")
    args = parser.parse_args()

    size = args.size
    runtime_flavor = runtime_flavor_suffix()

    set_output_filename(filename=f"mandelbrot_{size}_{runtime_flavor}")

    set_tag("start_mandelbrot")
    checksum = mandelbrot_checksum(size=size)
    set_tag("finish_mandelbrot")

    print(f"checksum: {checksum}")
