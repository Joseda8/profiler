#!/bin/bash


# Iterate over each combination of file_to_run and num_records
sleep 1
python3 -m src.main --file_to_run test_cases.projects.general.0.sleep --is_module
sleep 2
python3 -m src.main --file_to_run test_cases.projects.general.3.threads --is_module --script_args --num_threads 1
sleep 2
python3 -m src.main --file_to_run test_cases.projects.general.3.threads --is_module --script_args --num_threads 2
sleep 2
python3 -m src.main --file_to_run test_cases.projects.general.3.threads --is_module --script_args --num_threads 4
sleep 2
python3 -m src.main --file_to_run test_cases.projects.general.3.threads --is_module --script_args --num_threads 6
sleep 2
python3 -m src.main --file_to_run test_cases.projects.general.3.threads --is_module --script_args --num_threads 8
sleep 2
python3 -m src.main --file_to_run test_cases.projects.general.4.processes --is_module --script_args --num_processes 1
sleep 2
python3 -m src.main --file_to_run test_cases.projects.general.4.processes --is_module --script_args --num_processes 2
sleep 2
python3 -m src.main --file_to_run test_cases.projects.general.4.processes --is_module --script_args --num_processes 4
sleep 2
python3 -m src.main --file_to_run test_cases.projects.general.4.processes --is_module --script_args --num_processes 6
sleep 2
python3 -m src.main --file_to_run test_cases.projects.general.4.processes --is_module --script_args --num_processes 8
sleep 2


# Run post-profiling process
echo "Running post-profiling flow..."
python3 -m test_cases.projects.general.3.process_results
python3 -m test_cases.projects.general.4.process_results
