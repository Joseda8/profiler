#!/bin/bash

set -euo pipefail

RUN_ID=${1:-}
if [[ -n "$RUN_ID" ]]; then
  echo "Running Threaded Numerical scenarios (RUN_ID=$RUN_ID)"
else
  echo "Running Threaded Numerical scenarios"
fi

workers=(1 2 4 8 12)

# Factorial
for w in "${workers[@]}"; do
  python3 -m src.main --file_to_run test_cases.projects.energy_consumption.scenarios.threads_numerical.0.factorial --is_module --script_args --num_workers "$w" --max_value 10000 --run_idx "$RUN_ID"
  sleep 1
done

# Matmul
for w in "${workers[@]}"; do
  python3 -m src.main --file_to_run test_cases.projects.energy_consumption.scenarios.threads_numerical.1.matmul --is_module --script_args --matrix_size 768 --num_workers "$w" --run_idx "$RUN_ID"
  sleep 1
done

# Nbody
for w in "${workers[@]}"; do
  python3 -m src.main --file_to_run test_cases.projects.energy_consumption.scenarios.threads_numerical.2.nbody --is_module --script_args --num_particles 2000 --num_steps 10 --num_workers "$w" --run_idx "$RUN_ID"
  sleep 1
done
