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
    "test_cases.projects.pandas.v1.scenarios.0.*"
    "test_cases.projects.pandas.v1.scenarios.1.*"
)

# Define arrays of values
file_to_run_values=(
    "test_cases.projects.pandas.v1.scenarios.0.data_frame"
    "test_cases.projects.pandas.v1.scenarios.0.dictionary"
    "test_cases.projects.pandas.v1.scenarios.1.data_frame"
    "test_cases.projects.pandas.v1.scenarios.1.dictionary"
    "test_cases.projects.pandas.v1.scenarios.2.iterative"
    "test_cases.projects.pandas.v1.scenarios.2.non_iterative"
    "test_cases.projects.pandas.v1.scenarios.3.conversion_inside"
    "test_cases.projects.pandas.v1.scenarios.3.conversion_outside"
    "test_cases.projects.pandas.v1.scenarios.3.no_conversion"
    "test_cases.projects.pandas.v1.scenarios.4.len"
    "test_cases.projects.pandas.v1.scenarios.4.shape"
    "test_cases.projects.pandas.v1.scenarios.5.no_timezone"
    "test_cases.projects.pandas.v1.scenarios.5.timezone"
    "test_cases.projects.pandas.v1.scenarios.6.apply_dataframe"
    "test_cases.projects.pandas.v1.scenarios.6.apply_series"
    "test_cases.projects.pandas.v1.scenarios.6.map"
    "test_cases.projects.pandas.v1.scenarios.7.clean_input"
    "test_cases.projects.pandas.v1.scenarios.7.raw_input"
    "test_cases.projects.pandas.v1.scenarios.8.inplace_inline"
    "test_cases.projects.pandas.v1.scenarios.8.inplace_multiline"
    "test_cases.projects.pandas.v1.scenarios.8.not_inplace"
    "test_cases.projects.pandas.v1.scenarios.9.bool_index"
    "test_cases.projects.pandas.v1.scenarios.9.mask"
    "test_cases.projects.pandas.v1.scenarios.9.replace_copy"
    "test_cases.projects.pandas.v1.scenarios.9.replace_inplace"
    "test_cases.projects.pandas.v1.scenarios.10.copy_all"
    "test_cases.projects.pandas.v1.scenarios.10.copy_one"
    "test_cases.projects.pandas.v1.scenarios.10.copy_three"
    "test_cases.projects.pandas.v1.scenarios.10.inplace_all"
    "test_cases.projects.pandas.v1.scenarios.10.inplace_one"
    "test_cases.projects.pandas.v1.scenarios.10.inplace_three"
    "test_cases.projects.pandas.v1.scenarios.11.subset"
    "test_cases.projects.pandas.v1.scenarios.11.whole_set"
    "test_cases.projects.pandas.v1.scenarios.12.mask"
    "test_cases.projects.pandas.v1.scenarios.12.query"
    "test_cases.projects.pandas.v1.scenarios.13.modin"
    "test_cases.projects.pandas.v1.scenarios.13.pandas"
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
            # Run the Python profiler
            echo "Running test: $file_to_run with num_records: $num_records"
            python3 -m src.main --file_to_run "$file_to_run" --is_module --script_args --num_records "$num_records"
            sleep 2
        fi
    done
done

# Run post-profiling process
echo "Running post-profiling flow..."
python3 -m test_cases.projects.pandas.v1.process_results.main --path_results results/preprocessed/
