# System Profiler
## _Collect and record the behavior of a program_

This profilers is a Python-based tool designed to measure the performance and resource usage of a program. Right now it supports the profiling of Python programs as scripts or modules.

It collects various system statistics such as CPU usage, memory usage and execution time.

The profiler collects stats with an ideal sampling rate of 100ms. Also, since it triggers the process to profile without being part of it, the profiling process has a very low overhead.

> For now the project has been tested only on `Fedora 37` and `Ubuntu 24.04.3 LTS`.

## Features

- **Performance Measurement**: The profiler gathers the next system metrics:
    - Execution time.
    - CPU usage.
    - CPU usage per core (of the whole system and not only of the process to profile).
    - RAM usage.
    - Virtual memory usage.
    - Swap usage.
    - Energy consumption (system-wide cumulative energy counter via Intel RAPL / `powercap-info v0.6.0-1`).
- **Detailed Reports**: Profiling results are saved in CSV format to facilitate post-processing analysis. Additionally, the standard output of the program is captured and stored in a text file.
- **Post-processing interface**: The profiler contains an interface offering some tools to process the CSV file obtained from the profiling process.

## Usage

To profile a Python script or module, use the following command-line command:

```bash
python3 -m src.main --file_to_run <file_or_module_name> [--is_module] [--script_args <optional_args>]
````

* `<file_or_module_name>`: Specify the name of the Python script or module to profile.
* `--is_module`: Optional flag indicating whether the provided input is a module.
* `--script_args <optional_args>`: Optional arguments to pass to the script being profiled.

For example:

```bash
python3 -m src.main --file_to_run test_cases.projects.pandas.scenarios.0.data_frame --is_module --script_args --num_records 1000000
```

## Energy measurements

Energy measurements rely on Intel RAPL counters exposed through `powercap-info` (provided by the `powercap-utils` package).
By default, reading these counters requires root privileges. To avoid running the profiler with `sudo`, you can allow your user to run `powercap-info` without a password (tested on `Linux/Ubuntu 24.04.3 LTS`):

Run:

```bash
sudo visudo
```

Add a line:

```
yourusername ALL=(ALL) NOPASSWD: /usr/bin/powercap-info
```

## Examples

Check the `test_cases` folder for more elaborated examples using the profiler.
