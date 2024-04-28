from typing import Dict, Optional, Tuple, List
import re

import numpy as np
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
        self._num_cores = FileStats.count_cores_in_dataframe(df=self._df_stats)

        # Extra attributes
        self._gini_max = (self._num_cores - 1) / self._num_cores
        self._core_columns = [CSV_STATS_COL_NAME_CORE_N_USAGE.format(core_idx=idx) for idx in range(0, self._num_cores)]

    @staticmethod
    def count_cores_in_dataframe(df: pd.DataFrame) -> int:
        """
        Count the number of unique core identifiers (n) in the DataFrame based on column names.

        Args:
            start_label (pd.DataFrame): The input DataFrame containing columns representing core usage.

        Returns:
            int: The number of unique core identifiers found in the DataFrame column names.
        """
        # Pattern to match core_<n>_usage in column names
        pattern = r'^core_\d+_usage$'
        # Extract core identifiers from column names
        core_identifiers = {re.match(pattern, col).group(0) for col in df.columns if re.match(pattern, col)}
        num_cores = len(core_identifiers)
        return num_cores

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
        df_between_labels = self._df_stats.loc[start_indices[0]:finish_indices[0]].copy()

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
        average_cpu_usage = df_between_labels[CSV_STATS_COL_NAME_CPU_USAGE].mean()
        average_virtual_memory_usage = df_between_labels[CSV_STATS_COL_NAME_VIRTUAL_MEMORY_USAGE].mean()
        average_ram_usage = df_between_labels[CSV_STATS_COL_NAME_RAM_USAGE].mean()
        average_swap_usage = df_between_labels[CSV_STATS_COL_NAME_SWAP_USAGE].mean()
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
        min_virtual_memory_usage = df_between_labels[CSV_STATS_COL_NAME_VIRTUAL_MEMORY_USAGE].min()
        max_virtual_memory_usage = df_between_labels[CSV_STATS_COL_NAME_VIRTUAL_MEMORY_USAGE].max()
        min_ram_usage = df_between_labels[CSV_STATS_COL_NAME_RAM_USAGE].min()
        max_ram_usage = df_between_labels[CSV_STATS_COL_NAME_RAM_USAGE].max()
        min_swap_usage = df_between_labels[CSV_STATS_COL_NAME_SWAP_USAGE].min()
        max_swap_usage = df_between_labels[CSV_STATS_COL_NAME_SWAP_USAGE].max()

        return (min_virtual_memory_usage, max_virtual_memory_usage, min_ram_usage, max_ram_usage, min_swap_usage, max_swap_usage)

    def track_dominant_core_changes_between_labels(self, start_label: str, finish_label: str) -> Tuple[int, float, float]:
        """
        Track changes in the dominant core between specific labels and calculate the total time with dominant cores.

        Args:
            start_label (str): The starting label.
            finish_label (str): The finishing label.

        Returns:
            Optional[Tuple[int, float]]: A tuple containing the number of changes in the dominant core and the cumulative duration
            of each dominant core state in seconds. Also the average disparity of the cores load.
        """
        # Compute dominant cores between a given range
        df_between_labels = self._get_df_between_labels(start_label=start_label, finish_label=finish_label).reset_index()
        df_between_labels["dominant_core"] = df_between_labels.apply(self._find_dominant_core, axis=1)
        # Compute load disparity
        df_between_labels["core_load_disparity"] = df_between_labels.apply(self._get_cores_load_disparity, axis=1)
        cores_disparity_avg = df_between_labels[df_between_labels["core_load_disparity"] > 0]["core_load_disparity"].mean()
        cores_disparity_avg = 0 if cores_disparity_avg is np.NaN else cores_disparity_avg

        # Dominant core changes and cumulative duration
        dominant_core_changes = 0
        timer_dom_core = 0.0

        # Track changes and calculate duration of each dominant core state
        current_dominant_core = None
        dominant_core_start = None
        for idx, row in df_between_labels.iterrows():
            dominant_core = row["dominant_core"]
            if dominant_core >= 0:
                if dominant_core != current_dominant_core:
                    # Update dominant core change count
                    current_dominant_core = dominant_core
                    dominant_core_changes += 1
                    # Start timer for current dominant core state
                    dominant_core_start = row["uptime"] if dominant_core_start is None else dominant_core_start
                elif idx == len(df_between_labels) - 1:
                    # Calculate duration the dominant core that never changed
                    timer_dom_core += (row["uptime"] - dominant_core_start)
            else:
                # Update current dominant core value
                current_dominant_core = dominant_core
                # Calculate duration of the last dominant core state
                if dominant_core_start:
                    timer_dom_core += (row["uptime"] - dominant_core_start)
                    dominant_core_start = None

        return (dominant_core_changes, timer_dom_core, cores_disparity_avg)
    
    def _get_cores_load_disparity(self, row: pd.Series) -> float:
        """
        Calculate the load disparity among the cores.

        This function computes the Gini coefficient of the serie
        and scales the value to the maximum possible given the number
        of cores evaluated.

        Parameters:
        row (pd.Series): A pandas Series containing float numbers.

        Returns:
        float: A percentage of how much disparity there is in the record.
        """
        # Get usage per core
        usage_per_core = row[self._core_columns]

        total_usage = usage_per_core.sum()
        if total_usage > 0:
            # Normalize and sort the serie
            normalized_series = usage_per_core / usage_per_core.sum()
            normalized_series.sort_values(inplace=True)
            normalized_series.reset_index(drop=True, inplace=True)
            # Compute Σ(i * value_i)
            summation = ((normalized_series.index + 1) * normalized_series).sum()
            # Calculate Gini coefficient
            gini_coefficient = (2 * summation - self._num_cores - 1) / self._num_cores
            # Scale the value to the maximum Gini coefficient possible
            gini_coefficient_percentage = (gini_coefficient * 100) / self._gini_max
        else:
            gini_coefficient_percentage = 0
        return gini_coefficient_percentage

    def _find_dominant_core(self, row: pd.Series, threshold: int = 70) -> int:
        """
        Find the dominant core in a given row.

        Args:
            row (pd.Series): A pandas Series representing a row in the DataFrame.
            threshold (int, optional): The threshold for determining dominance. Defaults to 70.

        Returns:
            int: The index of the dominant core if found. -1 if there is no dominant core.
        """
        max_usage = 0
        dominant_core = -1
        for idx, core in enumerate(self._core_columns):
            if row[core] > max_usage and all(row[core] - row[other_core] >= threshold for other_core in self._core_columns if other_core != core):
                max_usage = row[core]
                dominant_core = idx
        return dominant_core
