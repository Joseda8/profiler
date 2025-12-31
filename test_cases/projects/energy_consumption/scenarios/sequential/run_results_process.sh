#!/bin/bash

set -euo pipefail

# Process both flavors to build a single summary with a flavor column
SUMMARY_DIR="results/processed"
mkdir -p "$SUMMARY_DIR"
python3 -m test_cases.projects.energy_consumption.process_results.main --pattern "results/preprocessed/mandelbrot_*_stats.csv" --output_file "$SUMMARY_DIR/sequential_mandelbrot_summary.csv" --task_label mandelbrot --variant_column size
python3 -m test_cases.projects.energy_consumption.process_results.main --pattern "results/preprocessed/bubble_sort_*_stats.csv" --output_file "$SUMMARY_DIR/sequential_bubble_sort_summary.csv" --task_label bubble_sort --variant_column num_items
python3 -m test_cases.projects.energy_consumption.process_results.main --pattern "results/preprocessed/prime_sieve_*_stats.csv" --output_file "$SUMMARY_DIR/sequential_prime_sieve_summary.csv" --task_label prime_sieve --variant_column limit
