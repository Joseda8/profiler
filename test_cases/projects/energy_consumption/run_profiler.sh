#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Running energy consumption scenarios (NumPy)..."
bash "$SCRIPT_DIR/scenarios/numpy/run_profiler.sh"

echo "Running energy consumption scenarios (Sequential)..."
bash "$SCRIPT_DIR/scenarios/sequential/run_profiler.sh"

echo "Running energy consumption scenarios (Threaded Objects)..."
bash "$SCRIPT_DIR/scenarios/threads_objects/run_profiler.sh"

echo "Running energy consumption scenarios (Threaded Numerical)..."
bash "$SCRIPT_DIR/scenarios/threads_numerical/run_profiler.sh"
