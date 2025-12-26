#!/bin/bash

set -euo pipefail

workers=(1 2 4 8 12)

# JSON parse (50k records)
for w in "${workers[@]}"; do
  python3 -m src.main --file_to_run test_cases.projects.energy_consumption.scenarios.threads_objects.0.json_parse --is_module --script_args --num_records 50000 --num_workers "$w"
  sleep 1
done

# Text tokenize (50k records)
for w in "${workers[@]}"; do
  python3 -m src.main --file_to_run test_cases.projects.energy_consumption.scenarios.threads_objects.1.text_tokenize --is_module --script_args --num_records 50000 --num_workers "$w"
  sleep 1
done

# Object lists (2M records)
for w in "${workers[@]}"; do
  python3 -m src.main --file_to_run test_cases.projects.energy_consumption.scenarios.threads_objects.2.object_lists --is_module --script_args --num_records 2000000 --num_workers "$w"
  sleep 1
done
