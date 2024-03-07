import os
from typing import Any, List

import pandas as pd


class FileWriterCsv:
    """
    A class for managing data and writing it to a CSV file.
    """

    def __init__(self, file_path: str, columns: List[str]):
        """
        Initialize FileWriterCsv with the file path and column names.

        Args:
            file_path (str): The path to the CSV file.
            columns (List[str]): List of column names.
        """
        self._file_path = file_path
        self._data = pd.DataFrame(columns=columns)

    def append_row(self, row_data: List[Any]) -> None:
        """
        Append a row to the data.

        Args:
            row_data (List[str]): Data for the new row.
        """
        new_row = pd.DataFrame([row_data], columns=self._data.columns)
        self._data = pd.concat([self._data, new_row], ignore_index=True)

    def write_to_csv(self) -> None:
        """
        Write the data to a CSV file.
        """
        # Check if the path exists and creates it otherwise
        directory = os.path.dirname(self._file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        # Save CSV file
        self._data.to_csv(self._file_path, index=False)
