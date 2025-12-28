#!/bin/bash

set -euo pipefail

# Process both flavors to build a single summary with a flavor column
SUMMARY_DIR="results/processed/summaries"
mkdir -p "$SUMMARY_DIR"
for variant in gil nogil; do
  python3 -m test_cases.projects.energy_consumption.process_results.main --pattern "results/preprocessed/numpy_vectorized_*_${variant}_*_stats.csv" --output_file "$SUMMARY_DIR/numpy_numpy_vectorized_summary.csv" --task_label numpy_vectorized --variant_column length --flavor "$variant"
  python3 -m test_cases.projects.energy_consumption.process_results.main --pattern "results/preprocessed/numpy_blas_*_${variant}_*_stats.csv" --output_file "$SUMMARY_DIR/numpy_numpy_blas_summary.csv" --task_label numpy_blas --variant_column size --flavor "$variant"
  python3 -m test_cases.projects.energy_consumption.process_results.main --pattern "results/preprocessed/numpy_fft_*_${variant}_*_stats.csv" --output_file "$SUMMARY_DIR/numpy_numpy_fft_summary.csv" --task_label numpy_fft --variant_column length --flavor "$variant"
done
