#!/bin/bash

set -euo pipefail

# Process both flavors to build a single summary with a flavor column
for variant in gil nogil; do
  python3 -m test_cases.projects.energy_consumption.process_results.main --pattern "results/preprocessed/mandelbrot_*_${variant}_*_stats.csv" --output_file "results/processed/sequential_mandelbrot_summary.csv" --task_label mandelbrot --variant_column size --flavor "$variant"
  python3 -m test_cases.projects.energy_consumption.process_results.main --pattern "results/preprocessed/bubble_sort_*_${variant}_*_stats.csv" --output_file "results/processed/sequential_bubble_sort_summary.csv" --task_label bubble_sort --variant_column num_items --flavor "$variant"
  python3 -m test_cases.projects.energy_consumption.process_results.main --pattern "results/preprocessed/prime_sieve_*_${variant}_*_stats.csv" --output_file "results/processed/sequential_prime_sieve_summary.csv" --task_label prime_sieve --variant_column limit --flavor "$variant"
done
