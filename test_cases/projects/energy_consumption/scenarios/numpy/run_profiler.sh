#!/bin/bash

set -euo pipefail

RUN_ID=${1:-}
if [[ -n "$RUN_ID" ]]; then
  echo "Running NumPy scenarios (RUN_ID=$RUN_ID)"
else
  echo "Running NumPy scenarios"
fi

# NumPy vectorized lengths
for length in 200000000 300000000 400000000 500000000 600000000; do
  python3 -m src.main --file_to_run test_cases.projects.energy_consumption.scenarios.numpy.0.numpy_vectorized --is_module --script_args --length "$length" --run_idx "$RUN_ID"
  sleep 1
done

# NumPy BLAS sizes
for size in 7500 10000 12500 15000 20000; do
  python3 -m src.main --file_to_run test_cases.projects.energy_consumption.scenarios.numpy.1.numpy_blas --is_module --script_args --size "$size" --run_idx "$RUN_ID"
  sleep 1
done

# NumPy FFT lengths
for length in 100000000 200000000 300000000 400000000 500000000; do
  python3 -m src.main --file_to_run test_cases.projects.energy_consumption.scenarios.numpy.2.numpy_fft --is_module --script_args --length "$length" --run_idx "$RUN_ID"
  sleep 1
done
