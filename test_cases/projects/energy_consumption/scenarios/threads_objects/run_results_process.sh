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

python3 -m test_cases.projects.energy_consumption.process_results.main --pattern "results/preprocessed/json_parse_*_${variant}_*_stats.csv" --output_file "results/processed/json_parse_summary_${variant}.csv" --task_label json_parse --variant_column num_workers
python3 -m test_cases.projects.energy_consumption.process_results.main --pattern "results/preprocessed/text_tokenize_*_${variant}_*_stats.csv" --output_file "results/processed/text_tokenize_summary_${variant}.csv" --task_label text_tokenize --variant_column num_workers
python3 -m test_cases.projects.energy_consumption.process_results.main --pattern "results/preprocessed/object_lists_*_${variant}_*_stats.csv" --output_file "results/processed/object_lists_summary_${variant}.csv" --task_label object_lists --variant_column num_workers
