#!/bin/bash

# Function to check if string matches any pattern
function matches_any_pattern() {
    local string="$1"
    local patterns=("${@:2}")

    for pattern in "${patterns[@]}"; do
        if [[ $string == $pattern ]]; then
            # Match found
            return 0
        fi
    done

    # No match found
    return 1
}

# List of scenarios to exclude to check against
excluded_scenarios=(
    "test_cases.projects.pandas.v2.scenarios.0.*"
)

# Define arrays of values
file_to_run_values=(
    "test_cases.projects.pandas.v2.scenarios.0.data_frame"
    "test_cases.projects.pandas.v2.scenarios.0.dictionary"
    "test_cases.projects.pandas.v2.scenarios.1.clean_input"
    "test_cases.projects.pandas.v2.scenarios.1.raw_input"
    "test_cases.projects.pandas.v2.scenarios.2.copy"
    "test_cases.projects.pandas.v2.scenarios.2.inplace"
    "test_cases.projects.pandas.v2.scenarios.3.subset"
    "test_cases.projects.pandas.v2.scenarios.3.whole_set"
    "test_cases.projects.pandas.v2.scenarios.4.mask"
    "test_cases.projects.pandas.v2.scenarios.4.query"
)

num_records_values=(
    10
    20
    50
    100
    500
    1000
    5000
    10000
    50000
    100000
    200000
    500000
    1000000
    2000000
)

# Iterate over each combination of file_to_run and num_records
sleep 1
for file_to_run in "${file_to_run_values[@]}"; do
    for num_records in "${num_records_values[@]}"; do
        # Check if the pattern must be excluded
        if [[ $num_records -eq 2000000 ]] && matches_any_pattern "$file_to_run" "${excluded_scenarios[@]}"; then
            # Skip the test
            echo "Skipping test: $file_to_run with num_records: $num_records"
        else
            # Run each test three times
            for run in {1..3}; do
                echo "Running test: $file_to_run with num_records: $num_records (Run $run)"
                python3 -m src.main --file_to_run "$file_to_run" --is_module --script_args --num_records "$num_records"
                sleep 2
            done
        fi
    done
done

# Run post-profiling process
echo "Running post-profiling flow..."
python3 -m test_cases.projects.pandas.v2.process_results.main --path_results results/preprocessed/
