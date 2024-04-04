from typing import Dict, Optional, Tuple, List

import pandas as pd

from .const import *


class FileStats:
    """
    A class for analyzing a CSV file with results from
    the profiler.
    """

    def __init__(self, file_path: str):
        """
        Initialize FileStats with the file path.

        Args:
            file_path (str): The path to the CSV file.
        """
        self._file_path = file_path
        self._df_stats = pd.read_csv(file_path)

    def _find_label_indices(self, label: str) -> List[int]:
        """
        Find the indices of a specific label in the dataframe.

        Args:
            label (str): The label to search for.

        Returns:
            List[int]: A list of indices where the label is found.
        """
        return self._df_stats.index[self._df_stats["label"] == label].tolist()

    def _get_df_between_labels(self, start_label: str, finish_label: str) -> Optional[pd.DataFrame]:
        """
        Extract the DataFrame between two labels.

        Args:
            start_label (str): The starting label.
            finish_label (str): The finishing label.

        Returns:
            Optional[pd.DataFrame]: DataFrame containing rows between start_label and finish_label indices.
        """
        # Find the indices of start_label and finish_label
        start_indices = self._find_label_indices(start_label)
        finish_indices = self._find_label_indices(finish_label)

        # Ensure start_label and finish_label are found in the dataframe
        if not start_indices or not finish_indices:
            return None

        # Extract rows between start_label and finish_label indices
        df_between_labels = self._df_stats.loc[start_indices[0]:finish_indices[0]]

        return df_between_labels

    def get_times(self, start_label: str, finish_label: str) -> Dict[str, float]:
        """
        Calculate time differences between start and finish tasks.

        Args:
            start_label (str): The starting label.
            finish_label (str): The finishing label.

        Returns:
            time_diff: A dictionary containing time differences for each task.
        """
        # Dictionary to store the time differences between labels
        time_diff: Dict[str, float] = {}

        # Create times-labels dictionary
        dict_labels_times = self._df_stats.dropna(subset=[CSV_STATS_COL_NAME_LABEL]).set_index(CSV_STATS_COL_NAME_LABEL)[CSV_STATS_COL_NAME_UPTIME].to_dict()

        for key in dict_labels_times:
            # Check if the key starts with the start label prefix
            if key.startswith(start_label):
                # Extract the task name from the key and create finish tag
                task_name = key[len(start_label):]
                finish_key = finish_label + task_name
                # Calculate the time difference and store it in the time_diff dictionary
                if finish_key in dict_labels_times:
                    time_diff[task_name] = dict_labels_times[finish_key] - dict_labels_times[key]
        return time_diff

    def get_average_between_labels(self, start_label: str, finish_label: str) -> Optional[Tuple[float, float, float, float]]:
        """
        Compute the average CPU usage and memory stats between two labels.

        Returns None if either of the labels was not found.

        Args:
            start_label (str): The starting label.
            finish_label (str): The finishing label.

        Returns:
            Optional[Tuple[float, float, float, float]]: If both labels are found, returns a tuple containing
            the average CPU usage, average virtual memory usage, average RAM usage,
            and average swap usage between the labels. If either label is not found, returns None.
        """
        # Extract rows between start_label and finish_label indices
        df_between_labels = self._get_df_between_labels(start_label=start_label, finish_label=finish_label)

        # Calculate the average CPU usage, virtual memory usage, RAM usage, and swap usage for the relevant rows
        average_cpu_usage = df_between_labels["cpu_usage"].mean()
        average_virtual_memory_usage = df_between_labels["virtual_memory_usage"].mean()
        average_ram_usage = df_between_labels["ram_usage"].mean()
        average_swap_usage = df_between_labels["swap_usage"].mean()
        return (average_cpu_usage, average_virtual_memory_usage, average_ram_usage, average_swap_usage)

    def get_min_max_memory_stats(self, start_label: str, finish_label: str) -> Optional[Tuple[float, float, float, float, float, float]]:
        """
        Get the minimum and maximum memory stats between two labels.

        Returns None if either of the labels was not found.

        Args:
            start_label (str): The starting label.
            finish_label (str): The finishing label.

        Returns:
            Optional[Tuple[float, float, float, float]]: If both labels are found, returns a tuple containing
            the minimum and maximum values of virtual memory usage, RAM usage,
            and swap usage between the labels. If either label is not found, returns None.
        """
        # Extract rows between start_label and finish_label indices
        df_between_labels = self._get_df_between_labels(start_label=start_label, finish_label=finish_label)

        # Calculate the minimum and maximum values of virtual memory usage, RAM usage, and swap usage for the relevant rows
        min_virtual_memory_usage = df_between_labels["virtual_memory_usage"].min()
        max_virtual_memory_usage = df_between_labels["virtual_memory_usage"].max()
        min_ram_usage = df_between_labels["ram_usage"].min()
        max_ram_usage = df_between_labels["ram_usage"].max()
        min_swap_usage = df_between_labels["swap_usage"].min()
        max_swap_usage = df_between_labels["swap_usage"].max()

        return (min_virtual_memory_usage, max_virtual_memory_usage, min_ram_usage, max_ram_usage, min_swap_usage, max_swap_usage)

    def track_dominant_core_changes_between_labels(self, start_label: str, finish_label: str) -> Optional[float]:
        """
        Track changes in the dominant core between specific labels and calculate the average duration between changes.

        Args:
            start_label (str): The starting label.
            finish_label (str): The finishing label.

        Returns:
            Optional[float]: The average duration between changes in the dominant core between the specified labels in seconds.
        """
        # Extract rows between start_label and finish_label indices
        df_between_labels = self._get_df_between_labels(start_label=start_label, finish_label=finish_label)

        # Find dominant core
        dominant_core_changes = 0
        current_dominant_core = None
        for _, row in df_between_labels.iterrows():
            dominant_core = self._find_dominant_core(row=row)
            if current_dominant_core and dominant_core:
                if dominant_core != current_dominant_core:
                    current_dominant_core = dominant_core
                    dominant_core_changes += 1
            else:
                current_dominant_core = dominant_core
        return dominant_core_changes


    def _find_dominant_core(self, row: pd.Series, threshold: int = 70) -> Optional[int]:
        """
        Find the dominant core in a given row.

        Args:
            row (pd.Series): A pandas Series representing a row in the DataFrame.
            threshold (int, optional): The threshold for determining dominance. Defaults to 70.

        Returns:
            Optional[int]: The index of the dominant core if found, None otherwise.
        """
        core_columns = ["core_1_usage", "core_2_usage", "core_3_usage", "core_4_usage", "core_5_usage", "core_6_usage"]
        max_usage = 0
        dominant_core = None
        for i, core in enumerate(core_columns):
            if row[core] > max_usage and all(row[core] - row[other_core] >= threshold for other_core in core_columns if other_core != core):
                max_usage = row[core]
                dominant_core = i + 1
        return dominant_core
