#!/bin/bash

set -euo pipefail

RUN_ID=${1:-}
if [[ -n "$RUN_ID" ]]; then
  echo "Running Threaded Objects scenarios (RUN_ID=$RUN_ID)"
else
  echo "Running Threaded Objects scenarios"
fi

workers=(1 2 4 8 12)

# JSON parse
for w in "${workers[@]}"; do
  python3 -m src.main --file_to_run test_cases.projects.energy_consumption.scenarios.threads_objects.0.json_parse --is_module --script_args --num_records 100000 --num_workers "$w" --run_idx "$RUN_ID"
  sleep 1
done

# Text tokenize
for w in "${workers[@]}"; do
  python3 -m src.main --file_to_run test_cases.projects.energy_consumption.scenarios.threads_objects.1.text_tokenize --is_module --script_args --num_records 100000 --num_workers "$w" --run_idx "$RUN_ID"
  sleep 1
done

# Object lists
for w in "${workers[@]}"; do
  python3 -m src.main --file_to_run test_cases.projects.energy_consumption.scenarios.threads_objects.2.object_lists --is_module --script_args --num_records 5000000 --num_workers "$w" --run_idx "$RUN_ID"
  sleep 1
done
