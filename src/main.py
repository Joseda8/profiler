import argparse

from .const import OUTPUT_FILE_PATH, STATS_FILE_PATH
from .system_stats_collector import SystemStatsCollector
from .util import FileWriterCsv, FileWriterTxt, logger, run_python_process, DatetimeHelper

# Parse terminal arguments
parser = argparse.ArgumentParser(description="Measure the performance of a given Python program.")
parser.add_argument("--file_to_run", required=True, help="Name of the file or module to run.")
parser.add_argument("--is_module", action='store_true', help="Flag indicating whether the provided input is a module.")
parser.add_argument("--script_args", nargs=argparse.REMAINDER, default=[], help="Optional arguments for the script to run")
args = parser.parse_args()

# Run the process and get PID
process = run_python_process(file_or_module=args.file_to_run, is_module=args.is_module, args=args.script_args)
pid = process.pid
logger.info(f"PID of the command: {pid}")

# Measure subprocess resources usage
profiler_measurer = SystemStatsCollector(pid=pid)
logger.info(f"Process creation time: {profiler_measurer.get_process_create_time()}")
file_stats = FileWriterCsv(file_path=STATS_FILE_PATH, columns=SystemStatsCollector.get_values_to_measure())
while process.poll() is None:
    # Collect stats
    execution_time = DatetimeHelper.current_datetime()
    cpu_usage = profiler_measurer.get_cpu_usage()
    cpu_usage_per_core = SystemStatsCollector.get_cpu_usage_per_core()
    memory_usage = profiler_measurer.get_ram_usage()

    # Append new stats if they were successfully collected
    if execution_time is not None and cpu_usage is not None and cpu_usage_per_core is not None and memory_usage is not None:
        new_stats = [execution_time, cpu_usage] + cpu_usage_per_core + list(memory_usage)
        file_stats.append_row(row_data=new_stats)
        logger.debug(f"New records were successfully written.")

# Write profiling results file
file_stats.write_to_csv()
logger.info(f"Profiling results saved to: {STATS_FILE_PATH}")

# Get and write the output of the subprocess once it finishes
output, error = process.communicate()
FileWriterTxt.write_text_to_file(file_path=OUTPUT_FILE_PATH, text=output.decode())
logger.info(f"Output saved to: {OUTPUT_FILE_PATH}")
