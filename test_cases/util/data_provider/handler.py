import json
import os

from typing import Union
from itertools import cycle, islice

import pandas as pd

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
            # Download users and create JSON file
            if not self._is_data_available:
                data_downloader = DataDownloader()
                data_downloader.download_users(file_path=FILE_PATH_BASE_JSON, num_results=5000)
                # Create CSV file
                self._json_to_csv(path_csv=FILE_PATH_BASE_CSV, path_json=FILE_PATH_BASE_JSON)
                # Mark data as available
                self._is_data_available = True
                logger.info("Data downloaded successfully")
            else:
                logger.info("Data is already available")
        except Exception as excep:
            logger.error(f"Failed downloading the data: {excep}")
            self._is_data_available = False

    @staticmethod
    def _json_to_csv(path_csv: str, path_json: str):
        """
        Takes the users data dictionary and stores its content in a CSV file. 
        It requires a JSON file with the data.

        Parameters:
            path_csv (str): Path to store the CSV file".
            path_json (str): Path to the JSON file with the original data".
        """
        try:
            # Read original JSON file
            records = []
            with open(path_json, "r") as json_file:
                records = json.load(json_file)

            # Flatten the nested structure for each record
            flat_records = []
            for record in records:
                flat_record = {
                    "gender": record.get("gender"),
                    "title": record.get("name", {}).get("title"),
                    "first_name": record.get("name", {}).get("first"),
                    "last_name": record.get("name", {}).get("last"),
                    "street_number": record.get("location", {}).get("street", {}).get("number"),
                    "street_name": record.get("location", {}).get("street", {}).get("name"),
                    "city": record.get("location", {}).get("city"),
                    "state": record.get("location", {}).get("state"),
                    "country": record.get("location", {}).get("country"),
                    "postcode": record.get("location", {}).get("postcode"),
                    "latitude": record.get("location", {}).get("coordinates", {}).get("latitude"),
                    "longitude": record.get("location", {}).get("coordinates", {}).get("longitude"),
                    "timezone_offset": record.get("location", {}).get("timezone", {}).get("offset"),
                    "timezone_description": record.get("location", {}).get("timezone", {}).get("description"),
                    "email": record.get("email"),
                    "username": record.get("login", {}).get("username"),
                    "password": record.get("login", {}).get("password"),
                    "dob": record.get("dob", {}).get("date"),
                    "age": record.get("dob", {}).get("age"),
                    "registered_date": record.get("registered", {}).get("date"),
                    "registered_age": record.get("registered", {}).get("age"),
                    "phone": record.get("phone"),
                    "cell": record.get("cell"),
                    "picture_large": record.get("picture", {}).get("large"),
                    "picture_medium": record.get("picture", {}).get("medium"),
                    "picture_thumbnail": record.get("picture", {}).get("thumbnail"),
                    "nationality": record.get("nat"),
                }
                flat_records.append(flat_record)

            # Convert the flat records to a Pandas DataFrame
            df = pd.DataFrame(flat_records)
            df.to_csv(path_csv, index=False)

        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error reading JSON file: {e}")
            return None

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

    def read_data(self, num_records: int, data_type: str, csv_column_types: dict = None) -> Union[pd.DataFrame, dict, None]:
        """
        Read data from either CSV or JSON format.

        Args:
            num_records (int): Number of records to read.
            data_type (str): Type of data to read. Can be 'csv' or 'json'.
            csv_column_types (dict): Optional argument to specify column types for CSV files.

        Returns:
            DataFrame or dict: DataFrame if data_type is 'csv', dict if data_type is 'json'.
        """
        if not self._is_data_available:
            logger.error("The base data has not been downloaded")
            return None
        elif data_type == "csv":
            file_path = FILE_PATH_BASE_CSV.replace("5000", str(num_records))
            try:
                if csv_column_types:
                    return pd.read_csv(file_path, dtype=csv_column_types)
                else:
                    return pd.read_csv(file_path)
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
    