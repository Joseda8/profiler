import json
import requests

from ...util.logger import logger

class DataDownloader:
    """
    Class to download dummy data about users.
    """

    def download_users(self, file_path: str, num_results: int = 5000):
        """
        Download user data from a public API and save it to a JSON file.

        Args:
            num_results (int, optional): Number of user records to download. Defaults to 5000 since this is the API limit.
            file_path (str): Path to store the downloaded data.
        """
        # API URL
        url = f"https://randomuser.me/api/?results={num_results}"

        try:
            # Get data
            logger.info("Downloading data...")
            response = requests.get(url)
            response.raise_for_status()
            users_data = response.json()["results"]

            # Write the data to a JSON file
            with open(file_path, "w") as json_file:
                json.dump(users_data, json_file, indent=2)
            logger.info(f"Downloaded {num_results} user records and saved to {file_path}.")
        except requests.exceptions.RequestException as excep:
            logger.info(f"Error downloading data: {excep}")
