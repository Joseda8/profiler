#!/bin/bash

set -euo pipefail

RUN_ID=${1:-}
if [[ -n "$RUN_ID" ]]; then
  echo "Running NumPy scenarios (RUN_ID=$RUN_ID)"
else
  echo "Running NumPy scenarios"
fi

# NumPy vectorized lengths
for length in 150000000 200000000 250000000 300000000 350000000 400000000 450000000; do
  python3 -m src.main --file_to_run test_cases.projects.energy_consumption.scenarios.numpy.0.numpy_vectorized --is_module --script_args --length "$length" --run_idx "$RUN_ID"
  sleep 5
done

# NumPy BLAS sizes
for size in 6000 7500 9000 10500 12000 13500 15000; do
  python3 -m src.main --file_to_run test_cases.projects.energy_consumption.scenarios.numpy.1.numpy_blas --is_module --script_args --size "$size" --run_idx "$RUN_ID"
  sleep 5
done

# NumPy FFT lengths
for length in 50000000 100000000 150000000 200000000 250000000 300000000 350000000; do
  python3 -m src.main --file_to_run test_cases.projects.energy_consumption.scenarios.numpy.2.numpy_fft --is_module --script_args --length "$length" --run_idx "$RUN_ID"
  sleep 5
done
