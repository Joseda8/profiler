"""
This benchmark sleeps to measure the overhead caused by the profiler.

Benchmark Steps:
1. Zzzz.
"""

import time
import os

import psutil

from src.client_interface import set_tag, set_output_filename

# Set output filename
set_output_filename(filename=f"{os.path.splitext(os.path.basename(__file__))[0]}")

# Measure memory usage
process = psutil.Process()
print(f"VMS (Virtual Memory Size): {process.memory_info().vms / (1024 * 1024):.2f} MB")
print(f"RAM: {process.memory_info().rss / (1024 * 1024):.2f} MB")

# Sleep
set_tag("start_sleep")
time.sleep(10)
set_tag("finish_sleep")
