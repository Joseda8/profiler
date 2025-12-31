#!/bin/bash

set -euo pipefail

# Process both flavors to build a single summary with a flavor column
SUMMARY_DIR="results/processed"
mkdir -p "$SUMMARY_DIR"
python3 -m test_cases.projects.energy_consumption.process_results.main --pattern "results/preprocessed/factorial_*_stats.csv" --output_file "$SUMMARY_DIR/threads_numerical_factorial_summary.csv" --task_label factorial --variant_column num_workers
python3 -m test_cases.projects.energy_consumption.process_results.main --pattern "results/preprocessed/matmul_*_stats.csv" --output_file "$SUMMARY_DIR/threads_numerical_matmul_summary.csv" --task_label matmul --variant_column num_workers
python3 -m test_cases.projects.energy_consumption.process_results.main --pattern "results/preprocessed/nbody_*_stats.csv" --output_file "$SUMMARY_DIR/threads_numerical_nbody_summary.csv" --task_label nbody --variant_column num_workers
