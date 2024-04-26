from typing import List, Optional, Tuple

import psutil

from .const import KEYWORD_CPU_USAGE_PER_CORE, TEMPLATE_USAGE_PER_CORE, VALUES_TO_MEASURE
from src.util import DatetimeHelper
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
        self._cpu_count = SystemStatsCollector.get_cpu_count()

    @staticmethod
    def get_values_to_measure() -> List[str]:
        """
        Get the name of the values that the profiler is able to return.

        TODO: This should check the OS in which is running.

        Returns:
            values_to_measure: Name of the values to measure.
        """
        # Build cores values
        values_cpu_usage = [TEMPLATE_USAGE_PER_CORE.format(core_idx=idx) for idx in range(SystemStatsCollector.get_cpu_count())]
        idx_cpu_cores_usage = VALUES_TO_MEASURE.index(KEYWORD_CPU_USAGE_PER_CORE)
        # Build stats values
        values_to_measure = VALUES_TO_MEASURE
        values_to_measure[idx_cpu_cores_usage:idx_cpu_cores_usage+1] = values_cpu_usage
        return values_to_measure
    
    def get_cpu_usage(self) -> Optional[float]:
        """
        Get the CPU usage of the process specified by the PID.

        It is measured in a gap of 0.1 seconds, so it is a blocking action.

        Returns:
            float: CPU usage percentage of the process.
                   Returns None if the process with the given PID does not exist.
        """
        try:
            process = psutil.Process(self._pid)
            cpu_usage = process.cpu_percent(interval=0.1) / self._cpu_count
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

    def get_memory_usage(self) -> Tuple[float, float, float]:
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

    def get_process_create_time(self) -> Optional[float]:
        """
        Get the time (from the epoch) when the process 
        specified by the PID was created.

        Returns:
            create_time: Time when the process was created.
                                None if the process with the given PID does not exist.
        """
        try:
            process = psutil.Process(self._pid)
            create_time = process.create_time()
            return create_time
        except psutil.NoSuchProcess:
            logger.error(f"Process with PID {self._pid} does not exist.")
            return None

    def get_measure_timestamp(self) -> float:
        """
        Get timestamp (from the epoch) of the current measure.

        Returns:
            timestamp: Current timestamp.
        """
        timestamp = DatetimeHelper.current_datetime(from_the_epoch=True)
        return timestamp

    def collect_stats(self) -> Optional[List]:
        """
        Collect stats for the current process.

        Returns:
            new_stats: Stats collected.
        """
        # Collect stats
        execution_time = self.get_measure_timestamp()
        cpu_usage = self.get_cpu_usage()
        cpu_usage_per_core = SystemStatsCollector.get_cpu_usage_per_core()
        memory_usage = self.get_memory_usage()
        
        # Return the measurements if all of them were successfully collected
        if execution_time is not None and cpu_usage is not None and cpu_usage_per_core is not None and memory_usage is not None:
            new_stats = [execution_time, cpu_usage] + cpu_usage_per_core + list(memory_usage)
            return new_stats
        else:
            return None
