import subprocess
import time

from .const import OUTPUT_FILE_PATH
from .util import FileWriter, logger


# Command to execute
command = "python3 /home/josemontoya/work/profiler/script.py"

# Run the command
process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)

# Get the PID of the triggered command
pid = process.pid
logger.info(f"PID of the command: {pid}")

# Perform some actions while the command is running
while process.poll() is None:
    logger.debug("Command is still running...")
    # Do something else while waiting
    time.sleep(1)

# Get the output once the command finishes
output, error = process.communicate()

# Specify the file path to save the output
output_file_path = f"{OUTPUT_FILE_PATH}/output.txt"

# Write the output to the file
FileWriter.write_text_to_file(file_path=output_file_path, text=output.decode())
logger.info(f"Output saved to: {output_file_path}")
