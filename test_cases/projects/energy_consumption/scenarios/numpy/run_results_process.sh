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

python3 -m test_cases.projects.energy_consumption.process_results.main --pattern "results/preprocessed/numpy_vectorized_*_${variant}_*_stats.csv" --output_file "results/processed/numpy_numpy_vectorized_summary_${variant}.csv" --task_label numpy_vectorized --variant_column length
python3 -m test_cases.projects.energy_consumption.process_results.main --pattern "results/preprocessed/numpy_blas_*_${variant}_*_stats.csv" --output_file "results/processed/numpy_numpy_blas_summary_${variant}.csv" --task_label numpy_blas --variant_column size
python3 -m test_cases.projects.energy_consumption.process_results.main --pattern "results/preprocessed/numpy_fft_*_${variant}_*_stats.csv" --output_file "results/processed/numpy_numpy_fft_summary_${variant}.csv" --task_label numpy_fft --variant_column length
