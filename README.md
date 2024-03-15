# System Profiler
## _Collect and record the behavior of a Python program_

The System Profiler is a Python-based tool designed to measure the performance and resource usage of a given Python program or module. It collects various system statistics such as CPU usage, RAM usage, and more, providing insights into the behavior and resource utilization of the target process.

> For now the project has been tested only on `Linux/Fedora 37`.

## Features

- **Comprehensive Performance Measurement**: The profiler gathers a wide range of system metrics, including CPU usage, RAM usage, and core-specific CPU usage.
- **Flexible Usage**: Users can specify the Python script or module to profile along with optional arguments, allowing for customizable profiling sessions.
- **Real-time Monitoring**: The profiler continuously monitors the target process, providing real-time statistics during its execution.
- **Detailed Reporting**: Profiling results are saved in CSV format for easy analysis, and output logs are captured for comprehensive reporting.

> Note: Notice that the project contains a `requirements.txt` file.

## Usage

To profile a Python script or module, use the following command-line interface:

```bash
python3 -m src.main --file_to_run <file_or_module_name> [--is_module] [--script_args <optional_args>]
```

- `<file_or_module_name>`: Specify the name of the Python script or module to profile.
- `--is_module`: Optional flag indicating whether the provided input is a module.
- `--script_args <optional_args>`: Optional arguments to pass to the script being profiled.

For example:

```bash
python3 -m src.main --file_to_run test_cases.tests.0.data_frame --is_module --script_args --num_records 1000000
```

## Examples

Check the `test_cases` folder for more elaborated examples using the profiler.
