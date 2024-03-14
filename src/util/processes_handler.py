import os
import subprocess
from typing import List

from . import logger


def run_python_process(file_or_module: str, is_module: bool, args: List[str] = []) -> subprocess.Popen:
    """
    Run a Python process.

    Args:
        file_or_module (str): Name of the file or module to run.
        is_module (bool): Flag indicating whether the provided input is a module.
        args (List[str], optional): List of terminal arguments to pass to the program. Default is [].

    Returns:
        subprocess.Popen: Popen object representing the running process.
    """
    # Verify that file or module exists
    file_path = f"{file_or_module.replace('.', '/')}.py" if is_module else file_or_module
    if not os.path.exists(file_path):
        logger.error(f"File or module '{file_path}' does not exist.")
        exit()

    # Run the process and get PID
    if is_module:
        command = f"python3 -m {file_or_module} {' '.join(args)}"
    else:
        command = f"python3 {file_or_module} {' '.join(args)}"

    return subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
