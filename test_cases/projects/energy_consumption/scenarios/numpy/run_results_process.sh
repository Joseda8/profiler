#!/bin/bash

set -euo pipefail

# Process both flavors to build a single summary with a flavor column
SUMMARY_DIR="results/processed"
mkdir -p "$SUMMARY_DIR"
python3 -m test_cases.projects.energy_consumption.process_results.main --pattern "results/preprocessed/numpy_vectorized_*_stats.csv" --output_file "$SUMMARY_DIR/numpy_vectorized_summary.csv" --task_label numpy_vectorized --variant_column length
python3 -m test_cases.projects.energy_consumption.process_results.main --pattern "results/preprocessed/numpy_blas_*_stats.csv" --output_file "$SUMMARY_DIR/numpy_blas_summary.csv" --task_label numpy_blas --variant_column size
python3 -m test_cases.projects.energy_consumption.process_results.main --pattern "results/preprocessed/numpy_fft_*_stats.csv" --output_file "$SUMMARY_DIR/numpy_fft_summary.csv" --task_label numpy_fft --variant_column length
