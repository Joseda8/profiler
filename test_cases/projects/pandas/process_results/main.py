from typing import Any, List, Tuple
import os
import re
from src.process_results import FileStats
from .const import *
from .data_plotter import DataPlotter
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
        self._path_input = folder_path
        self._files_info: Tuple[str, List[List[Tuple[str, str, int]]]] = []
        self._path_output = os.path.join(os.path.dirname(os.path.dirname(self._path_input)), "processed")

    @staticmethod
    def _get_stats_columns(time_tags: List[str]) -> List[str]:
        """
        Get the stats that were computed in a given file.

        Args:
            time_tags (str): Time tags that were extracted from the data.
        """
        time_tags = [f"time_{label}" for label in time_tags]
        stats_columns = STATS_COLUMNS.copy()
        stats_columns.pop(STATS_TIMES_ID_IDX)
        stats_columns = stats_columns[:STATS_TIMES_ID_IDX] + time_tags + stats_columns[STATS_TIMES_ID_IDX:]
        return stats_columns

    def _collect_file_names(self) -> None:
        """
        Collects the names of all files in the specified folder and organize them.
        """
        logger.info("Loading result files...")
        pattern = re.compile(r"(\d+)_(\w+)_([0-9]+)_(\d{8})_(\d{6})_stats\.csv")
        file_groups = {}

        for filename in os.listdir(self._path_input):
            file_path = os.path.join(self._path_input, filename)
            if os.path.isfile(file_path):
                match = pattern.match(filename)
                if match:
                    scenario_id = match.group(1)
                    file_type = match.group(2)
                    num_records = int(match.group(3))
                    if scenario_id not in file_groups:
                        file_groups[scenario_id] = []
                    file_groups[scenario_id].append((file_path, file_type, num_records))

        self._files_info = [(scenario_id, file_groups[scenario_id]) for scenario_id in sorted(file_groups.keys())]
        logger.info("Result files loaded.")

    def process_files(self) -> None:
        """
        Process all the files and generate final profiling results.
        """
        self._collect_file_names()

        # Create stats file
        for scenario_id, scenario_files in self._files_info:
            logger.info(f"Processing scenario: {scenario_id}")
            scenario_file_path = os.path.join(self._path_output, f"scenario_{scenario_id}.csv")
            csv_writer = FileWriterCsv(file_path=scenario_file_path)
            # Process one file at a time
            for file_path, test_name, num_records in scenario_files:
                stats, columns = self._process_file(file_path, test_name, num_records)
                if not csv_writer.have_columns():
                    csv_writer.set_columns(columns=columns)
                csv_writer.append_row(row_data=stats)
            csv_writer.write_to_csv()
        
        # After processing all files, create graphs for each scenario
        logger.info("Creating plots...")
        for scenario_id, _ in self._files_info:
            scenario_file_path = os.path.join(self._path_output, f"scenario_{scenario_id}.csv")
            plotter = DataPlotter(path_file_stats=scenario_file_path, folder_results=FOLDER_RESULTS_GRAPHS)
            # Plot various graphs for the scenario CSV
            for column in ["time_processing", "avg_cpu_usage", "avg_vm", "avg_ram", "avg_swap",
                           "min_vm", "max_vm", "min_ram", "max_ram", "min_swap", "max_swap", "core_changes_by_time"]:
                title = column.replace("_", " ").title() + " vs Number of Records"
                plotter.plot_line_graph(x_column="num_records", y_column=column, title=title)
            # Graph times
            time_columns = [col for col in plotter.stats_columns if col.startswith("time_") and col != f"time_{LABEL_PROGRAM}"]
            plotter.plot_bar_graphs(x_column="num_records", y_columns=time_columns, title="Time proportion per time")
        logger.info("Graphs created successfully.")
        
    def _process_file(self, file_path: str, test_name: str, num_records: int) -> Tuple[List[Any], List[str]]:
        """
        Process an individual file to extract statistics and append them to the CSV writer.

        Args:
            file_path (str): Path to the file being processed.
            test_name (str): Name of the test associated with the file.
            num_records (int): Number of records in the file.
            csv_writer (FileWriterCsv): Instance of FileWriterCsv to write results to.
        """
        logger.info(f"Processing file: {file_path}")
        current_file_stats = FileStats(file_path=file_path)
        uptimes = current_file_stats.get_times(start_label=LABEL_START_PREFIX, finish_label=LABEL_FINISH_PREFIX)
        averages = current_file_stats.get_average_between_labels(start_label=LABEL_START_PROGRAM, finish_label=LABEL_FINISH_PROGRAM)
        min_max = current_file_stats.get_min_max_memory_stats(start_label=LABEL_START_PROGRAM, finish_label=LABEL_FINISH_PROGRAM)
        dominant_core = current_file_stats.track_dominant_core_changes_between_labels(start_label=LABEL_START_PROGRAM, finish_label=LABEL_FINISH_PROGRAM)
        core_changes_by_time = dominant_core / uptimes[LABEL_PROGRAM]

        # Wrap up stats
        stats = [test_name, num_records] + list(uptimes.values()) + [averages[0], averages[1], averages[2], averages[3],
                                                                     min_max[0], min_max[1], min_max[2], min_max[3], min_max[4], min_max[5], 
                                                                     dominant_core, core_changes_by_time]

        # Get computed stats
        time_tags = list(uptimes.keys())
        stats_columns = FilesStats._get_stats_columns(time_tags=time_tags)
        return stats, stats_columns


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Process the results files given by the profiler.")
    parser.add_argument("--path_results", required=True, help="Path to the folder with the result files.")
    args = parser.parse_args()
    if not os.path.isdir(args.path_results):
        raise FileNotFoundError(f"Folder not found: {args.path_results}")

    # Process files
    files_stats = FilesStats(folder_path=args.path_results)
    files_stats.process_files()
