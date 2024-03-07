import argparse
import os
import subprocess

from .const import OUTPUT_FILE_PATH, STATS_FILE_PATH
from .system_stats_collector import SystemStatsCollector
from .util import FileWriterCsv, FileWriterTxt, logger


# Parse terminal arguments
parser = argparse.ArgumentParser(description="Measure the performance of a given Python program.")
parser.add_argument("--file_to_run", required=True, help="Name of the file to run.")
args = parser.parse_args()

# Verify that file exists
file_to_run = args.file_to_run
if not os.path.isfile(file_to_run):
    logger.error(f"File '{file_to_run}' does not exist.")
    exit()

# System stats to collect
name_stats_csv = SystemStatsCollector.get_values_to_measure()

# Run the process and get PID
command = f"python3 {file_to_run}"
process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
pid = process.pid
logger.info(f"PID of the command: {pid}")

# Measure subprocess resources usage
profiler_measurer = SystemStatsCollector(pid=pid)
file_stats = FileWriterCsv(file_path=STATS_FILE_PATH, columns=name_stats_csv)
while process.poll() is None:
    # Collect stats
    cpu_usage = profiler_measurer.get_cpu_usage()
    cpu_usage_per_core = SystemStatsCollector.get_cpu_usage_per_core()
    memory_usage = profiler_measurer.get_ram_usage()

    # Append new stats if they were successfully collected
    if cpu_usage is not None and cpu_usage_per_core is not None and memory_usage is not None:
        new_stats = [cpu_usage] + cpu_usage_per_core + list(memory_usage)
        file_stats.append_row(row_data=new_stats)
        logger.debug(f"New records were successfully written.")

# Write profiling results file
file_stats.write_to_csv()
logger.info(f"Profiling results saved to: {STATS_FILE_PATH}")

# Get and write the output of the subprocess once it finishes
output, error = process.communicate()
FileWriterTxt.write_text_to_file(file_path=OUTPUT_FILE_PATH, text=output.decode())
logger.info(f"Output saved to: {OUTPUT_FILE_PATH}")
