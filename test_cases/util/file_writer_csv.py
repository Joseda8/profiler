import os
from typing import Any, List
import pandas as pd

class FileWriterCsv:
    """
    A class for managing data and writing it to a CSV file.
    """

    def __init__(self, file_path: str):
        """
        Initialize FileWriterCsv with the file path.

        Args:
            file_path (str): The path to the CSV file.
        """
        self._file_path = file_path
        self._data = pd.DataFrame()

    def have_columns(self) -> bool:
        """
        Check if columns were already assigned.
        """
        does_have_columns = (len(self._data.columns)>0)
        return does_have_columns

    def set_columns(self, columns: List[str]) -> None:
        """
        Set the column names for the DataFrame.

        Args:
            columns (List[str]): List of column names.
        """
        if not self._data.empty:
            raise ValueError("Columns cannot be set once data has been appended.")
        self._data = pd.DataFrame(columns=columns)

    def append_row(self, row_data: List[Any]) -> None:
        """
        Append a row to the data.

        Args:
            row_data (List[Any]): Data for the new row.
        """
        if not self.have_columns():
            raise ValueError("Columns must be set before appending rows.")
        new_row = pd.DataFrame([row_data], columns=self._data.columns)
        self._data = pd.concat([self._data, new_row], ignore_index=True)

    def append_rows(self, rows_data: List[List[Any]]) -> None:
        """
        Append multiple rows to the data.

        Args:
            rows_data (List[List[Any]]): Data for the new rows.
        """
        if not self.have_columns():
            raise ValueError("Columns must be set before appending rows.")
        new_rows = pd.DataFrame(rows_data, columns=self._data.columns)
        self._data = pd.concat([self._data, new_rows], ignore_index=True)

    def write_to_csv(self) -> None:
        """
        Write the data to a CSV file.
        """
        if self._data.empty:
            raise ValueError("No data to write.")
        
        directory = os.path.dirname(self._file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        self._data.to_csv(self._file_path, index=False)
