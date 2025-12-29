#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Aggregating energy consumption results for both gil and nogil variants"
bash "$SCRIPT_DIR/scenarios/numpy/run_results_process.sh"
bash "$SCRIPT_DIR/scenarios/sequential/run_results_process.sh"
bash "$SCRIPT_DIR/scenarios/threads_objects/run_results_process.sh"
bash "$SCRIPT_DIR/scenarios/threads_numerical/run_results_process.sh"
