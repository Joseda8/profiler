import csv
import os
from typing import Any, List

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
        self._columns: List[str] = []
        self._rows: List[List[Any]] = []

    def have_columns(self) -> bool:
        """
        Check if columns were already assigned.
        """
        return len(self._columns) > 0

    def set_columns(self, columns: List[str]) -> None:
        """
        Set the column names for the DataFrame.

        Args:
            columns (List[str]): List of column names.
        """
        if self._rows:
            raise ValueError("Columns cannot be set once data has been appended.")
        self._columns = list(columns)

    def append_row(self, row_data: List[Any]) -> None:
        """
        Append a row to the data.

        Args:
            row_data (List[Any]): Data for the new row.
        """
        if not self.have_columns():
            raise ValueError("Columns must be set before appending rows.")
        self._rows.append(list(row_data))

    def append_rows(self, rows_data: List[List[Any]]) -> None:
        """
        Append multiple rows to the data.

        Args:
            rows_data (List[List[Any]]): Data for the new rows.
        """
        if not self.have_columns():
            raise ValueError("Columns must be set before appending rows.")
        for row in rows_data:
            if len(row) != len(self._columns):
                raise ValueError("Row length does not match number of columns.")
            self._rows.append(list(row))

    def order_by_columns(self, columns: List[str]) -> None:
        """
        Order the DataFrame by given columns.

        Args:
            columns (List[str]): The names of the columns to order by.
        """
        if not self.have_columns():
            raise ValueError("Columns must be set before ordering.")
        for column_name in columns:
            if column_name not in self._columns:
                raise ValueError(f"Column '{column_name}' does not exist in the data.")
        self._rows.sort(key=lambda row: tuple(row[self._columns.index(col)] for col in columns))

    def write_to_csv(self) -> None:
        """
        Write the data to a CSV file.
        """
        if not self._rows:
            raise ValueError("No data to write.")
        
        directory = os.path.dirname(self._file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        with open(self._file_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(self._columns)
            writer.writerows(self._rows)
