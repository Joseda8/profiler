"""
This benchmark sleeps to measure the overhead caused by the profiler.

Benchmark Steps:
1. Zzzz.
"""

import time
import os

from src.client_interface import set_tag, set_output_filename

# Set output filename
set_output_filename(filename=f"{os.path.splitext(os.path.basename(__file__))[0]}")

# Sleep
set_tag("start_sleep")
time.sleep(10)
set_tag("finish_sleep")
