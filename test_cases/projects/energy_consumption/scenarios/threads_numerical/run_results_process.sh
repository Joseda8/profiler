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

python3 -m test_cases.projects.energy_consumption.process_results.main --pattern "results/preprocessed/factorial_*_${variant}_*_stats.csv" --output_file "results/processed/factorial_summary_${variant}.csv" --task_label factorial --variant_column num_workers
python3 -m test_cases.projects.energy_consumption.process_results.main --pattern "results/preprocessed/matmul_*_${variant}_*_stats.csv" --output_file "results/processed/matmul_summary_${variant}.csv" --task_label matmul --variant_column num_workers
python3 -m test_cases.projects.energy_consumption.process_results.main --pattern "results/preprocessed/nbody_*_${variant}_*_stats.csv" --output_file "results/processed/nbody_summary_${variant}.csv" --task_label nbody --variant_column num_workers
