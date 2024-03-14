import json
import requests


def download_users(num_results=5000):
    """
    Download user data from a public API and save it to a JSON file.

    Args:
        num_results (int, optional): Number of user records to download. Defaults to 5000 since this is the API limit.
    """
    # API URL
    url = f"https://randomuser.me/api/?results={num_results}"

    try:
        # Get data
        print("Downloading data...")
        response = requests.get(url)
        response.raise_for_status()
        users_data = response.json()["results"]

        # Write the data to a JSON file
        file_path = "testing_data/users_data.json"
        with open(file_path, "w") as json_file:
            json.dump(users_data, json_file, indent=2)
        print(f"Downloaded {num_results} user records and saved to {file_path}.")
    except requests.exceptions.RequestException as excep:
        print(f"Error downloading data: {excep}")

if __name__ == "__main__":
    download_users()
