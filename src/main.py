import argparse
import os
import subprocess

from .const import OUTPUT_FILE_PATH
from .resources_measurer import ResourcesMeasurer
from .util import FileWriter, logger


# Parse terminal arguments
parser = argparse.ArgumentParser(description="Measure the performance of a given Python program.")
parser.add_argument("--file_to_run", required=True, help="Name of the file to run.")
args = parser.parse_args()

# Verify that file exists
file_to_run = args.file_to_run
if not os.path.isfile(file_to_run):
    logger.error(f"File '{file_to_run}' does not exist.")
    exit()

# Run the process and get PID
command = f"python3 {file_to_run}"
process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
pid = process.pid
logger.info(f"PID of the command: {pid}")

# Measure subprocess resources usage
profiler_measurer = ResourcesMeasurer(pid=pid)
while process.poll() is None:
    # Get general CPU usage
    cpu_usage = profiler_measurer.get_cpu_usage()
    logger.debug(f"CPU Usage: {cpu_usage}%")

# Get and write the output of the subprocess once it finishes
output, error = process.communicate()
FileWriter.write_text_to_file(file_path=OUTPUT_FILE_PATH, text=output.decode())
logger.info(f"Output saved to: {OUTPUT_FILE_PATH}")
