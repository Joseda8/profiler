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
        self.df_data = pd.DataFrame()

    def have_columns(self) -> bool:
        """
        Check if columns were already assigned.
        """
        return len(self.df_data.columns) > 0

    def set_columns(self, columns: List[str]) -> None:
        """
        Set the column names for the DataFrame.

        Args:
            columns (List[str]): List of column names.
        """
        if not self.df_data.empty:
            raise ValueError("Columns cannot be set once data has been appended.")
        self.df_data = pd.DataFrame(columns=columns)

    def append_row(self, row_data: List[Any]) -> None:
        """
        Append a row to the data.

        Args:
            row_data (List[Any]): Data for the new row.
        """
        if not self.have_columns():
            raise ValueError("Columns must be set before appending rows.")
        new_row = pd.DataFrame([row_data], columns=self.df_data.columns)
        # If data is empty, directly assign to it
        if self.df_data.empty:
            self.df_data = new_row
        # If not empty, concatenate normally
        else:
            self.df_data = pd.concat([self.df_data, new_row], ignore_index=True)

    def append_rows(self, rows_data: List[List[Any]]) -> None:
        """
        Append multiple rows to the data.

        Args:
            rows_data (List[List[Any]]): Data for the new rows.
        """
        if not self.have_columns():
            raise ValueError("Columns must be set before appending rows.")
        new_rows = pd.DataFrame(rows_data, columns=self.df_data.columns)
        # If data is empty, directly assign to it
        if self.df_data.empty:
            self.df_data = new_rows
        # If not empty, concatenate normally
        else:
            self.df_data = pd.concat([self.df_data, new_rows], ignore_index=True)

    def order_by_columns(self, columns: List[str]) -> None:
        """
        Order the DataFrame by given columns.

        Args:
            columns (List[str]): The names of the columns to order by.
        """
        if not self.have_columns():
            raise ValueError("Columns must be set before ordering.")
        for column_name in columns:
            if column_name not in self.df_data.columns:
                raise ValueError(f"Column '{column_name}' does not exist in the DataFrame.")
        self.df_data = self.df_data.sort_values(by=columns)

    def write_to_csv(self) -> None:
        """
        Write the data to a CSV file.
        """
        if self.df_data.empty:
            raise ValueError("No data to write.")
        
        directory = os.path.dirname(self._file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        self.df_data.to_csv(self._file_path, index=False)

    def set_data_frame(self, df: pd.DataFrame) -> None:
        """
        Set the DataFrame for the FileWriterCsv instance.

        Args:
            df (pd.DataFrame): The DataFrame to set.
        """
        if not df.empty and not self.df_data.empty:
            raise ValueError("DataFrame cannot be set once data has been appended.")
        self.df_data = df
