#!/bin/bash

# Define arrays of values
file_to_run_values=(
    "test_cases.projects.pandas.scenarios.0.data_frame"
    "test_cases.projects.pandas.scenarios.0.dictionary"
    "test_cases.projects.pandas.scenarios.1.data_frame"
    "test_cases.projects.pandas.scenarios.1.dictionary"
    "test_cases.projects.pandas.scenarios.2.iterative"
    "test_cases.projects.pandas.scenarios.2.non_iterative"
    "test_cases.projects.pandas.scenarios.3.conversion_inside"
    "test_cases.projects.pandas.scenarios.3.conversion_outside"
    "test_cases.projects.pandas.scenarios.3.no_conversion"
    "test_cases.projects.pandas.scenarios.4.len"
    "test_cases.projects.pandas.scenarios.4.shape"
)
num_records_values=(
    100
    500
    1000
    5000
    10000
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
        # Run the Python profiler
        echo "Running test: $file_to_run with num_records: $num_records"
        python3 -m src.main --file_to_run "$file_to_run" --is_module --script_args --num_records "$num_records"
        sleep 2
    done
done

# Run post-profiling process
echo "Running post-profiling flow..."
python3 -m test_cases.projects.pandas.process_results.main --path_results results/preprocessed/
