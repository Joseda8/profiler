#!/bin/bash

set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <gil|nogil>"
  exit 1
fi

variant="$1"
if [[ "$variant" != "gil" && "$variant" != "nogil" ]]; then
  echo "Variant must be 'gil' or 'nogil'"
  exit 1
fi

python3 -m test_cases.projects.energy_consumption.process_results.main --pattern "results/preprocessed/mandelbrot_*_${variant}_*_stats.csv" --output_file "results/processed/mandelbrot_summary_${variant}.csv" --task_label mandelbrot --variant_column size
python3 -m test_cases.projects.energy_consumption.process_results.main --pattern "results/preprocessed/bubble_sort_*_${variant}_*_stats.csv" --output_file "results/processed/bubble_sort_summary_${variant}.csv" --task_label bubble_sort --variant_column num_items
python3 -m test_cases.projects.energy_consumption.process_results.main --pattern "results/preprocessed/prime_sieve_*_${variant}_*_stats.csv" --output_file "results/processed/prime_sieve_summary_${variant}.csv" --task_label prime_sieve --variant_column limit
