import json
import os

from typing import List, Union
from itertools import cycle, islice

import pandas as pd
import modin.pandas as mpd

from ...util.logger import logger
from .downloader import DataDownloader


FOLDER_PATH_DATA = "test_cases/util/data_provider/data"
FILE_PATH_BASE_JSON = f"{FOLDER_PATH_DATA}/users_data_5000.json"
FILE_PATH_BASE_CSV = f"{FOLDER_PATH_DATA}/users_data_5000.csv"

class DataHandler:
    """
    A class to handle user data in several ways.
    """

    def __init__(self):
        """
        Initialize DataHandler.
        """
        self._is_data_available = self._check_file_existence(file_path=FILE_PATH_BASE_JSON) and self._check_file_existence(file_path=FILE_PATH_BASE_CSV)

    def _check_file_existence(self, file_path: str) -> bool:
        """
        Check if a file exists at the given file path.
        
        Args:
            file_path (str): Path to the file to check.
        
        Returns:
            bool: True if the file exists, False otherwise.
        """
        return os.path.isfile(file_path)

    def download_data(self):
        """
        Use the DataDownloader class to download users information and update the
        '_is_data_available' attribute.
        """
        try:
            # Download users and create base CSV/JSON file
            if not self._is_data_available:
                data_downloader = DataDownloader()
                data_downloader.download_users(file_path=FILE_PATH_BASE_JSON, file_type="json", num_results=5000)
                data_downloader.download_users(file_path=FILE_PATH_BASE_CSV, file_type="csv", num_results=5000)
                # Mark data as available
                self._is_data_available = True
                logger.info("Data downloaded successfully")
            else:
                logger.info("Data is already available")
        except Exception as excep:
            logger.error(f"Failed downloading the data: {excep}")
            self._is_data_available = False

    def extend_data(self, num_records: int):
        """
        Extend the existing data by creating/removing records in both JSON and CSV files.

        Args:
            num_records (int): Number of records to add.
        """
        try:
            # Extend JSON data
            self._extend_json_data(num_records=num_records)
            # Extend CSV data
            self._extend_csv_data(num_records=num_records)
            logger.info(f"Extended data by {num_records} records successfully")
        except Exception as excep:
            logger.error(f"Failed extending the data: {excep}")

    def _extend_json_data(self, num_records: int):
        """
        Extend JSON data by creating/removing records.

        Args:
            num_records (int): Number of records to add.
        """
        try:
            with open(FILE_PATH_BASE_JSON, "r") as json_file:
                records = json.load(json_file)
                # If num_records is less than the total number of records, cut the list
                if num_records < len(records):
                    records = records[:num_records]
                # If num_records is more than the total number of records, add duplicates
                elif num_records > len(records):
                    records = list(islice(cycle(records), num_records))
                # Write result
                new_file_path = FILE_PATH_BASE_JSON.replace("5000", str(num_records))
                with open(new_file_path, "w") as extended_json_file:
                    json.dump(records, extended_json_file)
        except Exception as excep:
            logger.error(f"Failed extending JSON data: {excep}")

    def _extend_csv_data(self, num_records: int):
        """
        Extend CSV data by creating/removing records.

        Args:
            num_records (int): Number of records to add.
        """
        try:
            # Read CSV data into a DataFrame
            df = pd.read_csv(FILE_PATH_BASE_CSV)
            
            # If num_records is less than the total number of records, cut the DataFrame
            if num_records < len(df):
                df = df.head(num_records)
            # If num_records is more than the total number of records, add duplicates
            elif num_records > len(df):
                repetitions = (num_records // len(df))
                df = pd.concat([df] * repetitions, ignore_index=True)
                df = df.head(num_records)
            # Write result
            new_file_path = FILE_PATH_BASE_CSV.replace("5000", str(num_records))
            df.to_csv(new_file_path, index=False)
        except Exception as excep:
            logger.error(f"Failed extending CSV data: {excep}")

    def read_data(self, num_records: int, data_type: str, csv_column_types: dict = None, use_modin: bool = False) -> Union[pd.DataFrame, List, None]:
        """
        Read data from either CSV or JSON format.

        Args:
            num_records (int): Number of records to read.
            data_type (str): Type of data to read. Can be 'csv' or 'json'.
            csv_column_types (dict): Optional argument to specify column types for CSV files.
            use_moding (bool): Whether Modin should be used or not for the CSV reading.

        Returns:
            DataFrame or list: DataFrame if data_type is 'csv', list of dictionaries if data_type is 'json'.
        """
        if not self._is_data_available:
            logger.error("The base data has not been downloaded")
            return None
        elif data_type == "csv":
            file_path = FILE_PATH_BASE_CSV.replace("5000", str(num_records))
            try:
                read_csv = mpd.read_csv if use_modin else pd.read_csv
                if csv_column_types:
                    return read_csv(file_path, dtype=csv_column_types)
                else:
                    return read_csv(file_path)
            except FileNotFoundError:
                logger.error(f"CSV file not found: {file_path}")
                return None
        elif data_type == "json":
            file_path = FILE_PATH_BASE_JSON.replace("5000", str(num_records))
            try:
                with open(file_path, "r") as json_file:
                    return json.load(json_file)
            except FileNotFoundError:
                logger.error(f"JSON file not found: {file_path}")
                return None
        else:
            logger.error("Invalid data type. Please choose either 'csv' or 'json'.")
            return None


if __name__ == "__main__":
    data_handler = DataHandler()

    # Download base data
    data_handler.download_data()

    # Replicate or cut base data to create new files
    logger.info("Creating files with different extensions")
    data_handler.extend_data(num_records=10)
    data_handler.extend_data(num_records=20)
    data_handler.extend_data(num_records=50)
    data_handler.extend_data(num_records=100)
    data_handler.extend_data(num_records=500)
    data_handler.extend_data(num_records=1000)
    data_handler.extend_data(num_records=5000)
    data_handler.extend_data(num_records=10000)
    data_handler.extend_data(num_records=50000)
    data_handler.extend_data(num_records=100000)
    data_handler.extend_data(num_records=200000)
    data_handler.extend_data(num_records=500000)
    data_handler.extend_data(num_records=1000000)
    data_handler.extend_data(num_records=2000000)
