#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

RUN_ID=${1:-$(date +%s)}
export RUN_ID
echo "Using RUN_ID=$RUN_ID for profiling outputs"

echo "Running energy consumption scenarios (NumPy)..."
bash "$SCRIPT_DIR/scenarios/numpy/run_profiler.sh" "$RUN_ID"

echo "Running energy consumption scenarios (Sequential)..."
bash "$SCRIPT_DIR/scenarios/sequential/run_profiler.sh" "$RUN_ID"

echo "Running energy consumption scenarios (Threaded Objects)..."
bash "$SCRIPT_DIR/scenarios/threads_objects/run_profiler.sh" "$RUN_ID"

echo "Running energy consumption scenarios (Threaded Numerical)..."
bash "$SCRIPT_DIR/scenarios/threads_numerical/run_profiler.sh" "$RUN_ID"
