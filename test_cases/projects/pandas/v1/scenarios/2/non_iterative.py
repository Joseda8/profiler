"""
This benchmark counters the number of users per country in a Pandas 
suitable way.

Benchmark Steps:
1. Load user data into a Pandas DataFrame with a specified number of records.
2. Use groupby and size to compute the value.
3. Measure and log the execution time for the operation.
"""

import argparse
import time
import os

from src.client_interface import set_tag, set_output_filename
from ......util import DataHandler, logger, get_scenario_name


# Use argparse to get num_records from the terminal
parser = argparse.ArgumentParser(description="Perform a test.")
parser.add_argument("--num_records", required=True, type=int, help="Number of records to process")
args = parser.parse_args()
num_records = args.num_records

# Set output filename
file_path = os.path.abspath(__file__)
scenario_name = get_scenario_name(file_path=file_path)
set_output_filename(filename=f"{scenario_name}_{num_records}")

# Idle time to ensure that the whole program is profiled
time.sleep(1)
set_tag("start_program")

#------- Extract data
data_handler = DataHandler()
num_records = args.num_records

set_tag("start_reading")
df_users = data_handler.read_data(num_records=num_records, data_type="csv")
set_tag("finish_reading")
logger.info(f"The required information was loaded successfully. Number of records: {len(df_users)}")

#------- Operation
set_tag("start_processing")

# Group by country, year, and month, then count the occurrences
df_country_year_month_registration = df_users.groupby(["location.country"]).size().reset_index(name="count")

set_tag("finish_processing")

# Idle time to ensure some last measures are taken
set_tag("finish_program")
time.sleep(1)
