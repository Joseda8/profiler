#!/bin/bash

set -euo pipefail

# Mandelbrot sizes
for size in 500 750 1000 1500 2000; do
  python3 -m src.main --file_to_run test_cases.projects.energy_consumption.scenarios.sequential.0.mandelbrot --is_module --script_args --size "$size"
  sleep 1
done

# Bubble sort item counts
for num_items in 5000 10000 15000 20000 30000; do
  python3 -m src.main --file_to_run test_cases.projects.energy_consumption.scenarios.sequential.1.bubble_sort --is_module --script_args --num_items "$num_items"
  sleep 1
done

# Prime sieve limits
for limit in 10000000 15000000 20000000 25000000 30000000; do
  python3 -m src.main --file_to_run test_cases.projects.energy_consumption.scenarios.sequential.2.prime_sieve --is_module --script_args --limit "$limit"
  sleep 1
done
