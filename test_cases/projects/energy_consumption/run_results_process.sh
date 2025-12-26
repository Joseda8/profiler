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

echo "Aggregating energy consumption results for variant: $variant"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

bash "$SCRIPT_DIR/scenarios/numpy/run_results_process.sh" "$variant"
bash "$SCRIPT_DIR/scenarios/sequential/run_results_process.sh" "$variant"
bash "$SCRIPT_DIR/scenarios/threads_objects/run_results_process.sh" "$variant"
bash "$SCRIPT_DIR/scenarios/threads_numerical/run_results_process.sh" "$variant"
