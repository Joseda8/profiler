#!/bin/bash

set -euo pipefail

# NumPy vectorized lengths
for length in 50000000 75000000 100000000 125000000 150000000; do
  python3 -m src.main --file_to_run test_cases.projects.energy_consumption.scenarios.numpy.0.numpy_vectorized --is_module --script_args --length "$length"
  sleep 1
done

# NumPy BLAS sizes
for size in 5000 7500 10000 12500 15000; do
  python3 -m src.main --file_to_run test_cases.projects.energy_consumption.scenarios.numpy.1.numpy_blas --is_module --script_args --size "$size"
  sleep 1
done

# NumPy FFT lengths
for length in 20000000 30000000 40000000 50000000 60000000; do
  python3 -m src.main --file_to_run test_cases.projects.energy_consumption.scenarios.numpy.2.numpy_fft --is_module --script_args --length "$length"
  sleep 1
done
