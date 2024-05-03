import csv
import json
import requests
from ...util.logger import logger

class DataDownloader:
    """
    Class to download dummy data about users.
    """

    def download_users(self, file_path: str, file_type: str, num_results: int = 5000):
        """
        Download user data from a public API and save it to a JSON or CSV file.

        Args:
            file_path (str): Path to store the downloaded data.
            file_type (str): Extension of the file to be downloaded, either "json" or "csv".
            num_results (int, optional): Number of user records to download. Defaults to 5000 since this is the API limit.
        """
        # API URL
        url = f"https://randomuser.me/api/?results={num_results}&format={file_type}&seed=love_sloths"

        try:
            # Get data
            logger.info("Downloading data...")
            response = requests.get(url)
            response.raise_for_status()

            if file_type.lower() == "json":
                users_data = response.json()["results"]
                with open(file_path, "w") as json_file:
                    json.dump(users_data, json_file, indent=2)
            elif file_type.lower() == "csv":
                with open(file_path, "wb") as csv_file:
                    csv_file.write(response.content)
            else:
                logger.error("Unsupported file type. Only JSON and CSV are supported.")
                return

            logger.info(f"Downloaded {num_results} user records and saved to {file_path}.")
        except requests.exceptions.RequestException as excep:
            logger.error(f"Error downloading data: {excep}")
