"""
This benchmark performs a series of DataFrame operations using not inplace methods.

Benchmark Steps:
1. Load user data into a Pandas DataFrame with a specified number of records.
2. Rename the column `location.street.number` to `street_number`.
3. Sort the DataFrame by the `dob.age` column.
4. Reset the index of the DataFrame.
5. Measure and log the execution time for the operation.
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

# Rename a column
df_users = df_users.rename(columns={"location.street.number": "street_number"})
# Order by age
df_users = df_users.sort_values(by="dob.age")
# Reset index
df_users = df_users.reset_index(drop=True)

set_tag("finish_processing")

# Idle time to ensure some last measures are taken
set_tag("finish_program")
time.sleep(1)
