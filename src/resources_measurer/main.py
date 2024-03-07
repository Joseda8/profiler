import psutil

from src.util import logger


class ResourcesMeasurer:
    """
    A class for measuring system resources for a given process.
    """

    def __init__(self, pid: int):
        """
        Initialize ResourcesMeasurer with the PID of the process to monitor.

        Args:
            pid (int): Process ID (PID) of the process to monitor.
        """
        self._pid = pid

    def get_cpu_usage(self) -> float:
        """
        Get the CPU usage of the process specified by the PID.

        It is measured in a gap of 0.1 seconds, so it is a blocking action.

        Returns:
            float: CPU usage percentage of the process.
                   Returns None if the process with the given PID does not exist.
        """
        try:
            process = psutil.Process(self._pid)
            cpu_usage = process.cpu_percent(interval=0.1)
            return cpu_usage
        except psutil.NoSuchProcess:
            logger.error(f"Process with PID {self._pid} does not exist.")
            return None
