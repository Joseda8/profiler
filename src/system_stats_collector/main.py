from typing import List, Optional, Tuple
import psutil
from src.util import logger


class SystemStatsCollector:
    """
    A class for measuring system resources for a given process.
    """

    def __init__(self, pid: int):
        """
        Initialize SystemStatsCollector with the PID of the process to monitor.

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

    @staticmethod
    def get_cpu_usage_per_core() -> Optional[List[float]]:
        """
        Get the CPU usage percentage for each CPU core.
        This method captures the core usage in general, that means that
        it is not possible to know which core is performing an action related to the
        given PID.

        It is measured in a gap of 0.1 seconds, so it is a blocking action.

        Returns:
            cpu_percentages: CPU usage percentage for each CPU core.
        """
        try:
            cpu_percentages = psutil.cpu_percent(percpu=True, interval=0.1)
            return cpu_percentages
        except Exception as excep:
            logger.error(f"Failed to retrieve CPU usage per core: {excep}")
            return None

    def get_ram_usage(self) -> Tuple[int, int, int]:
        """
        Get the RAM usage of the process specified by the PID.

        Returns:
            float: RAM usage in bytes of the process.
                   Returns None if the process with the given PID does not exist.
        """
        try:
            process = psutil.Process(self._pid)
            memory_usage = process.memory_full_info()
            # Convert values to GB
            virtual_memory_usage = memory_usage.vms / (1024 ** 3)
            ram_usage = memory_usage.rss / (1024 ** 3)
            swap_memory_usage = memory_usage.swap / (1024 ** 3)
            return (virtual_memory_usage, ram_usage, swap_memory_usage)
        except psutil.NoSuchProcess:
            logger.error(f"Process with PID {self._pid} does not exist.")
            return None

    @staticmethod
    def get_cpu_count() -> int:
        """
        Get the number of CPUs available in the system.

        Returns:
            int: Number of CPUs available.
        """
        return psutil.cpu_count()

    @staticmethod
    def get_values_to_measure() -> List[str]:
        """
        Get the name of the values that the profiler is able to return.

        TODO: This should check the OS in which is running.

        Returns:
            values_to_measure: Name of the values to measure.
        """
        values_to_measure = ["cpu_usage"] + [f"core_{i+1}_usage" for i in range(SystemStatsCollector.get_cpu_count())] + ["virtual_memory_usage", "ram_usage", "swap_usage"]
        return values_to_measure
