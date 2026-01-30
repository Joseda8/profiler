#!/bin/bash

set -euo pipefail

RUN_ID=${1:-}
if [[ -n "$RUN_ID" ]]; then
  echo "Running Sequential scenarios (RUN_ID=$RUN_ID)"
else
  echo "Running Sequential scenarios"
fi

# Mandelbrot sizes
for size in 500 1000 1500 2000 2500 3000 3500; do
  python3 -m src.main --file_to_run test_cases.projects.energy_consumption.scenarios.sequential.0.mandelbrot --is_module --script_args --size "$size" --run_idx "$RUN_ID"
  sleep 60
done

# Bubble sort item counts
for num_items in 5000 8000 11000 14000 17000 21000 25000; do
  python3 -m src.main --file_to_run test_cases.projects.energy_consumption.scenarios.sequential.1.bubble_sort --is_module --script_args --num_items "$num_items" --run_idx "$RUN_ID"
  sleep 60
done

# Prime sieve limits
for limit in 16000000 20000000 24000000 28000000 32000000 36000000 40000000; do
  python3 -m src.main --file_to_run test_cases.projects.energy_consumption.scenarios.sequential.2.prime_sieve --is_module --script_args --limit "$limit" --run_idx "$RUN_ID"
  sleep 60
done
