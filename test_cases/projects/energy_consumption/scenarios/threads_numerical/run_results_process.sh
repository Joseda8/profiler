#!/bin/bash

set -euo pipefail

# Process both flavors to build a single summary with a flavor column
SUMMARY_DIR="results/processed/summaries"
mkdir -p "$SUMMARY_DIR"
for variant in gil nogil; do
  python3 -m test_cases.projects.energy_consumption.process_results.main --pattern "results/preprocessed/factorial_*_${variant}_*_stats.csv" --output_file "$SUMMARY_DIR/threads_numerical_factorial_summary.csv" --task_label factorial --variant_column num_workers --flavor "$variant"
  python3 -m test_cases.projects.energy_consumption.process_results.main --pattern "results/preprocessed/matmul_*_${variant}_*_stats.csv" --output_file "$SUMMARY_DIR/threads_numerical_matmul_summary.csv" --task_label matmul --variant_column num_workers --flavor "$variant"
  python3 -m test_cases.projects.energy_consumption.process_results.main --pattern "results/preprocessed/nbody_*_${variant}_*_stats.csv" --output_file "$SUMMARY_DIR/threads_numerical_nbody_summary.csv" --task_label nbody --variant_column num_workers --flavor "$variant"
done
