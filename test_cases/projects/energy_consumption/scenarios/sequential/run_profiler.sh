#!/bin/bash

set -euo pipefail

RUN_ID=${1:-}
if [[ -n "$RUN_ID" ]]; then
  echo "Running Sequential scenarios (RUN_ID=$RUN_ID)"
else
  echo "Running Sequential scenarios"
fi

# Mandelbrot sizes
for size in 1000 1500 2000 3000 5000; do
  python3 -m src.main --file_to_run test_cases.projects.energy_consumption.scenarios.sequential.0.mandelbrot --is_module --script_args --size "$size" --run_idx "$RUN_ID"
  sleep 1
done

# Bubble sort item counts
for num_items in 7500 10000 15000 20000 30000; do
  python3 -m src.main --file_to_run test_cases.projects.energy_consumption.scenarios.sequential.1.bubble_sort --is_module --script_args --num_items "$num_items" --run_idx "$RUN_ID"
  sleep 1
done

# Prime sieve limits
for limit in 20000000 25000000 30000000 35000000 40000000; do
  python3 -m src.main --file_to_run test_cases.projects.energy_consumption.scenarios.sequential.2.prime_sieve --is_module --script_args --limit "$limit" --run_idx "$RUN_ID"
  sleep 1
done
