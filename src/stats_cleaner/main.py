from typing import Dict, List, Tuple
import csv
from src.const import PREFIX_MEASURE_TAG, PREFIX_MEASURE_TAG_FILE_NAME
from src.util import FileWriterCsv


class StatsCleaner:
    """
    Process the collected data after the program execution.
    """

    def __init__(self, stats_file: str, program_output_file: str) -> None:
        """
        Initialize StatsCleaner with the paths to the stats file and the output file.

        Args:
            stats_file (str): Path to the stats file.
            program_output_file (str): Path to the output file containing labels and timestamps.
        """
        self._stats_file = stats_file 
        self._program_output_file = program_output_file
        # List to store labels and timestamps
        self._labels: List[Tuple[str, float]] = []
        # List to store rows of stats data
        self._rows_stats: List[Dict] = []
        # List to store columns of the CSV file
        self._file_columns: List[str] = []
        # Output CSV file after processing
        self._output_csv_path: str = None

    def _read_program_output_file(self) -> None:
        """
        Read the output file containing labels and timestamps.
        Extracts labels and timestamps and stores them in the labels list.
        """
        with open(self._program_output_file, "r") as file:
            for line in file:
                if line.startswith(PREFIX_MEASURE_TAG_FILE_NAME):
                    # Split each line by colon and whitespace
                    label, filename = line.strip().split(": ")
                    self._output_csv_path = filename
                
                elif line.startswith(PREFIX_MEASURE_TAG):
                    # Split each line by colon and whitespace
                    label, timestamp = line.strip().split(": ")
                    label = label.replace(PREFIX_MEASURE_TAG, "")
                    self._labels.append((label, float(timestamp)))

    def _read_stats_file(self) -> None:
        """
        Read the stats file and store the rows in _rows_stats.
        """
        with open(self._stats_file, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            # Store rows and columns
            self._rows_stats = list(reader)
            self._file_columns = list(self._rows_stats[0].keys()) + ["label"]

    def _assign_labels(self) -> None:
        """
        Assign labels to rows in the stats file based on timestamps.

        For each label and timestamp pair, finds the closest row in the stats file
        based on the "uptime" column and assigns the label to a duplicated row.
        Stores the updated data in the _rows_stats attribute.
        """
        # For each label and timestamp pair, assign label to the closest row
        for label, timestamp in self._labels:
            closest_row = min(self._rows_stats, key=lambda row: abs(float(row["uptime"]) - timestamp))
            duplicated_row = closest_row.copy()
            duplicated_row["uptime"] = timestamp
            duplicated_row["label"] = label
            self._rows_stats.append(duplicated_row)

    def _update_uptime(self, process_creation_time: float) -> None:
        """
        Convert the uptime column from seconds from the epoch to seconds from
        the creation of the process.

        Args:
            process_creation_time (float): Time when the process was created given in seconds from the epoch.
        """
        # For each label and timestamp pair, assign label to the closest row
        for row in self._rows_stats:
            row["uptime"] = float(row["uptime"]) - process_creation_time

    def run(self, output_csv_path: str, process_creation_time: float) -> None:
        """
        Run the cleaning process.

        Writes the cleaned data to a CSV file.

        Args:
            output_csv_path (str): Path to the CSV file to write the cleaned data.
            process_creation_time (float): Time when the process was created given in seconds from the epoch.
        """
        # Read input files
        self._read_program_output_file()
        self._read_stats_file()

        # Assign labels to the stats
        self._assign_labels()

        # Convert uptime column to seconds from the start of the program
        self._update_uptime(process_creation_time=process_creation_time)

        # Add possible filename prefix to the output CSV
        output_csv_path_split = output_csv_path.split("/")
        file_name = f"{self._output_csv_path}_{output_csv_path_split[-1]}" if self._output_csv_path else output_csv_path_split[-1]
        output_csv_path = "/".join(output_csv_path_split[:-1] + [file_name])

        # Write the sorted rows to a CSV file using FileWriterCsv
        self._rows_stats = sorted(self._rows_stats, key=lambda row: float(row["uptime"]))
        file_writer = FileWriterCsv(file_path=output_csv_path, columns=self._file_columns)
        file_writer.append_rows(rows_data=self._rows_stats)
        file_writer.write_to_csv()
