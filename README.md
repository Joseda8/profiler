# System Profiler
## _Collect and record the behavior of a program_

This profiler is a Python-based tool designed to measure the performance and resource usage of a program. Right now it supports the profiling of Python programs as scripts or modules.

The profiler collects stats with an ideal sampling rate of 50ms. Also, since it triggers the process to profile without being part of it, the profiling process has a very low overhead.

> For now the project has been tested only on `Fedora 37` and `Ubuntu 24.04.3 LTS`.

## Features

- **Performance Measurement**: The profiler collects the next system metrics:
    - Execution time.
    - CPU usage.
    - CPU usage per core (system-wide stat).
    - RSS.
    - VMS.
    - Swap.
    - Energy consumption (system-wide cumulative energy counter via Intel RAPL).
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
python3 -m src.main --file_to_run test_cases.projects.general.0.sleep --is_module
```

## Energy measurements
Energy measurements rely on Intel RAPL via the Linux sysfs interface. By default, reading these counters requires root privileges. To avoid running the profiler with `sudo`, you can configure persistent read access to Intel RAPL energy counters (tested on `Linux/Ubuntu 24.04.3 LTS`).

Run:

```bash
# Create "power" group if it does not exist
getent group power || sudo groupadd power
getent group power

# Add current user to the group
sudo usermod -aG power $USER
groups | grep power
```

Create tmpfiles rule:

```bash
sudo nano /etc/tmpfiles.d/intel-rapl.conf

# Add the line
z /sys/class/powercap/intel-rapl:*/energy_uj 0444 root power -
```

Then run and verify these outputs:

```bash
sudo cat /etc/tmpfiles.d/intel-rapl.conf
sudo systemd-tmpfiles --create

# Verify permissions
ls -l /sys/class/powercap/intel-rapl:1/energy_uj

# Read energy counter
cat /sys/class/powercap/intel-rapl:1/energy_uj
```

## Examples

Check the `test_cases` folder for some examples using the profiler.
