from typing import List, Tuple

import argparse
import os
import re

from src.process_results import FileStats

from .const import *
from ....util import FileWriterCsv, logger


class FilesStats:
    """
    Class to collect and process file names from a given folder.
    """

    def __init__(self, folder_path: str) -> None:
        """
        Initialize FilesStats with the path to the folder containing files.

        Args:
            folder_path (str): Path to the folder containing files.
        """
        self._folder_path = folder_path
        self._files_info: Tuple[str, List[List[Tuple[str, str, int]]]] = []

    def _collect_file_names(self) -> None:
        """
        Collects the names of all files in the specified folder and organize them.
        """
        logger.info("Loading result files...")
        # Regular expression pattern to extract components from filenames
        pattern = re.compile(r"(\d+)_(\w+)_([0-9]+)_(\d{8})_(\d{6})_stats\.csv")

        # Dictionary to group filenames by scenario_id
        file_groups = {}

        # Collect file names
        for filename in os.listdir(self._folder_path):
            file_path = os.path.join(self._folder_path, filename)
            if os.path.isfile(file_path):
                match = pattern.match(filename)
                if match:
                    scenario_id = match.group(1)
                    file_type = match.group(2)
                    num_records = int(match.group(3))
                    # Append filename to corresponding scenario_id group
                    if scenario_id not in file_groups:
                        file_groups[scenario_id] = []
                    file_groups[scenario_id].append((file_path, file_type, num_records))

        # Organize file groups into self._files_info list
        self._files_info = [(scenario_id, file_groups[scenario_id]) for scenario_id in sorted(file_groups.keys())]
        logger.info("Result files loaded.")

    def process_files(self) -> None:
        """
        Process all the files creating the final profiling results.
        """
        # Load files information
        self._collect_file_names()
        
        # Process each scenario independently
        for scenario_id, scenario_files in self._files_info:
            logger.info(f"Processing scenario: {scenario_id}")
            folder_results = f"{os.path.dirname(os.path.dirname(self._folder_path))}/processed"
            scenario_file_path = os.path.join(folder_results, f"scenario_{scenario_id}.csv")
            file_writer = FileWriterCsv(file_path=scenario_file_path, columns=["test_name", "num_records",
                                                                               "time_program", "time_reading", "time_processing", 
                                                                               "avg_cpu_usage", "avg_vm", "avg_ram", "avg_swap",
                                                                               "min_vm", "max_vm", "min_ram", "max_ram", "min_swap", "max_swap",
                                                                               "dominant_core_changes"])
            # Process each file
            for file_path, test_name, num_records in scenario_files:
                # Extract stats
                logger.info(f"Processing file: {file_path}")
                file_stats: FileStats = FileStats(file_path=file_path)
                # Perform necessary computations with FileStats
                uptimes = file_stats.get_times(start_label=LABEL_START_PREFIX, finish_label=LABEL_FINISH_PREFIX)
                averages = file_stats.get_average_between_labels(start_label=LABEL_START_PROGRAM, finish_label=LABEL_FINISH_PROGRAM)
                min_max = file_stats.get_min_max_memory_stats(start_label=LABEL_START_PROGRAM, finish_label=LABEL_FINISH_PROGRAM)
                dominant_core = file_stats.track_dominant_core_changes_between_labels(start_label=LABEL_START_PROGRAM, finish_label=LABEL_FINISH_PROGRAM)

                # Append results to FileWriterCsv
                file_writer.append_row([test_name, num_records, 
                                        uptimes["program"], uptimes["reading"], uptimes["processing"],
                                        averages[0], averages[1], averages[2], averages[3],
                                        min_max[0], min_max[1], min_max[2], min_max[3], min_max[4], min_max[5],
                                        dominant_core])
            # Write scenario results to CSV file
            file_writer.write_to_csv()


if __name__ == "__main__":
    # Setup command-line argument parser
    parser = argparse.ArgumentParser(description="Process the results files given by the profiler.")
    parser.add_argument("--path_results", required=True, help="Path to the folder with the result files.")
    args = parser.parse_args()

    # Ensure the folder path is valid
    if not os.path.isdir(args.path_results):
        raise FileNotFoundError(f"Folder not found: {args.path_results}")

    # Instantiate FilesStats object with the provided folder path
    files_stats = FilesStats(folder_path=args.path_results)
    files_stats.process_files()
