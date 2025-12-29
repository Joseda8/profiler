#!/bin/bash

set -euo pipefail

# Process both flavors to build a single summary with a flavor column
SUMMARY_DIR="results/processed"
mkdir -p "$SUMMARY_DIR"
for variant in gil nogil; do
  python3 -m test_cases.projects.energy_consumption.process_results.main --pattern "results/preprocessed/json_parse_*_${variant}_*_stats.csv" --output_file "$SUMMARY_DIR/threads_objects_json_parse_summary.csv" --task_label json_parse --variant_column num_workers --flavor "$variant"
  python3 -m test_cases.projects.energy_consumption.process_results.main --pattern "results/preprocessed/text_tokenize_*_${variant}_*_stats.csv" --output_file "$SUMMARY_DIR/threads_objects_text_tokenize_summary.csv" --task_label text_tokenize --variant_column num_workers --flavor "$variant"
  python3 -m test_cases.projects.energy_consumption.process_results.main --pattern "results/preprocessed/object_lists_*_${variant}_*_stats.csv" --output_file "$SUMMARY_DIR/threads_objects_object_lists_summary.csv" --task_label object_lists --variant_column num_workers --flavor "$variant"
done
